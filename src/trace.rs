use std::fs::{File, OpenOptions};
use std::io::{self, Write};
use std::path::{Path, PathBuf};

use std::fs::{metadata, rename};

pub fn initialize_brz_log_filename() -> Result<PathBuf, std::io::Error> {
    let brz_log = std::env::var("BRZ_LOG").ok();
    if let Some(brz_log) = brz_log {
        Ok(PathBuf::from(brz_log))
    } else {
        let cache_dir = crate::bedding::cache_dir()?;
        Ok(cache_dir.join("brz.log"))
    }
}

pub fn rollover_trace_maybe(trace_fname: &Path) -> io::Result<()> {
    /// Roll over the trace log file if it exceeds a certain size.

    const MAX_LOG_SIZE: u64 = 4 * (1 << 20); // 4 MB

    let size = metadata(trace_fname)?.len();
    if size <= MAX_LOG_SIZE {
        return Ok(());
    }

    let old_fname = trace_fname.with_extension("log.old");
    rename(trace_fname, old_fname)?;
    Ok(())
}

/// Open existing log file, or create with ownership and permissions
///
/// It inherits the ownership and permissions (masked by umask) from the containing directory
/// to cope better with being run under sudo with `$HOME` still set to the user's homedir.
pub fn open_or_create_log_file<P: AsRef<Path>>(filename: P) -> std::io::Result<File> {
    let mut flags = OpenOptions::new();

    flags.append(true);

    loop {
        match flags.open(filename.as_ref()) {
            Ok(fd) => return Ok(fd),
            Err(e) if e.kind() == io::ErrorKind::NotFound => {
                let mut flags = OpenOptions::new();
                flags.create(true).truncate(true).write(true);

                match flags.open(&filename) {
                    Ok(fd) => {
                        // Copy ownership from containing directory.
                        breezy_osutils::file::copy_ownership_from_path(&filename, None)?;
                        return Ok(fd);
                    }
                    Err(e) if e.kind() == io::ErrorKind::AlreadyExists => continue,
                    Err(e) => return Err(e),
                }
            }
            Err(e) => return Err(e),
        }
    }
}

static mut BRZ_LOG_FILENAME: Option<PathBuf> = None;

pub fn get_brz_log_filename() -> Option<PathBuf> {
    unsafe { BRZ_LOG_FILENAME.clone() }
}

pub fn set_brz_log_filename(filename: Option<&Path>) {
    unsafe { BRZ_LOG_FILENAME = filename.map(|p| p.to_path_buf()) };
}

/// Open the brz.log trace file.
///
/// If the log is more than a particular length, the old file is renamed to `brz.log.old`
/// and a new file is started. Otherwise, we append to the existing file.
///
/// This sets the global `_brz_log_filename`.
pub fn open_brz_log() -> Option<File> {
    let filename = initialize_brz_log_filename().ok()?;
    unsafe { BRZ_LOG_FILENAME = Some(filename.clone()) };
    rollover_trace_maybe(&filename).ok();

    let mut brz_log_file = match open_or_create_log_file(&filename) {
        Ok(fd) => fd,
        Err(e) => {
            // If we are failing to open the log, then most likely logging has not
            // been set up yet. So we just write to stderr rather than using 'warning()'.
            // If we use warning(), users get the unhelpful 'no handlers registered for "brz"'
            // when something goes wrong on the server. (bug #503886)
            eprintln!("failed to open trace file: {}: {}", filename.display(), e);
            return None;
        }
    };

    // Write a header to the log file if it is empty.
    if brz_log_file
        .metadata()
        .ok()
        .map_or(false, |md| md.len() == 0)
    {
        if let Err(e) = writeln!(
            brz_log_file,
            "this is a debug log for diagnosing/reporting problems in brz"
        ) {
            eprintln!("failed to write to trace file: {}", e);
        }
        if let Err(e) = writeln!(
            brz_log_file,
            "you can delete or truncate this file, or include sections in"
        ) {
            eprintln!("failed to write to trace file: {}", e);
        }
        if let Err(e) = writeln!(
            brz_log_file,
            "bug reports to https://bugs.launchpad.net/brz/+filebug"
        ) {
            eprintln!("failed to write to trace file: {}", e);
        }
    }

    Some(brz_log_file)
}
