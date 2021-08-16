use pyo3::prelude::*;

fn main() -> PyResult<()> {
    const BIN_VERSION: &'static str = env!("CARGO_PKG_VERSION");

    Python::with_gil(|py| {
        let os = PyModule::import(py, "os")?;
        let locale = PyModule::import(py, "locale")?;

        if os.getattr("name")?.to_string() == "posix" {
            locale.getattr("setlocale")?.call1((locale.getattr("LC_ALL")?, "", ))?;
        }

        let sys = PyModule::import(py, "sys")?;

        sys.setattr("_brz_default_fs_enc", "utf-8")?;

        let breezy = PyModule::import(py, "breezy")?;

        let module_version = breezy.getattr("_core_version_string")?.to_string();

        if module_version != BIN_VERSION {
            println!("Mismatched versions: {}, {}", module_version, BIN_VERSION);
        }

        let main = PyModule::import(py, "breezy.__main__")?;
        main.getattr("main")?.call1(())?;
        Ok(())
    })
}

// profiling = False
// if '--profile-imports' in sys.argv:
//     import profile_imports
//     profile_imports.install()
//     profiling = True
// 
// 
// if os.name == "posix":
//     import locale
//     try:
//         locale.setlocale(locale.LC_ALL, '')
//     except locale.Error as e:
//         sys.stderr.write(
//             'brz: warning: %s\n'
//             '  bzr could not set the application locale.\n'
//             '  Although this should be no problem for bzr itself, it might\n'
//             '  cause problems with some plugins. To investigate the issue,\n'
//             '  look at the output of the locale(1p) tool.\n' % e)
//     # Use better default than ascii with posix filesystems that deal in bytes
//     # natively even when the C locale or no locale at all is given. Note that
//     # we need an immortal string for the hack, hence the lack of a hyphen.
//     sys._brz_default_fs_enc = "utf8"
// 
// 
// try:
//     import breezy
// except ImportError as e:
//     sys.stderr.write(
//         "brz: ERROR: "
//         "Couldn't import breezy and dependencies.\n"
//         "Please check the directory containing breezy is on your PYTHONPATH.\n"
//         "\n")
//     raise
// 
// if breezy.version_info[:3] != _script_version:
//     sys.stderr.write(
//         "brz: WARNING: breezy version doesn't match the brz program.\n"
//         "This may indicate an installation problem.\n"
//         "breezy is version %s from %s\n"
//         "brz is version %s from %s\n" % (
//             breezy._format_version_tuple(breezy.version_info),
//             breezy.__path__[0],
//             breezy._format_version_tuple(_script_version),
//             __file__))
// 
// if __name__ == '__main__':
//     from breezy.__main__ import main
//     main()
// else:
//     raise ImportError("The brz script cannot be imported.")
