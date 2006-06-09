/* Generated by Pyrex 0.9.3.1 on Sat Jun 10 02:07:45 2006 */

#include "Python.h"
#include "structmember.h"
#ifndef PY_LONG_LONG
  #define PY_LONG_LONG LONG_LONG
#endif
#include "errno.h"
#include "sys/types.h"
#include "dirent.h"
#include "readdir.h"


typedef struct {PyObject **p; char *s;} __Pyx_InternTabEntry; /*proto*/
typedef struct {PyObject **p; char *s; long n;} __Pyx_StringTabEntry; /*proto*/
static PyObject *__Pyx_UnpackItem(PyObject *, int); /*proto*/
static int __Pyx_EndUnpack(PyObject *, int); /*proto*/
static int __Pyx_PrintItem(PyObject *); /*proto*/
static int __Pyx_PrintNewline(void); /*proto*/
static void __Pyx_Raise(PyObject *type, PyObject *value, PyObject *tb); /*proto*/
static void __Pyx_ReRaise(void); /*proto*/
static PyObject *__Pyx_Import(PyObject *name, PyObject *from_list); /*proto*/
static PyObject *__Pyx_GetExcValue(void); /*proto*/
static int __Pyx_ArgTypeTest(PyObject *obj, PyTypeObject *type, int none_allowed, char *name); /*proto*/
static int __Pyx_TypeTest(PyObject *obj, PyTypeObject *type); /*proto*/
static int __Pyx_GetStarArgs(PyObject **args, PyObject **kwds, char *kwd_list[], int nargs, PyObject **args2, PyObject **kwds2); /*proto*/
static void __Pyx_WriteUnraisable(char *name); /*proto*/
static void __Pyx_AddTraceback(char *funcname); /*proto*/
static PyTypeObject *__Pyx_ImportType(char *module_name, char *class_name, long size);  /*proto*/
static int __Pyx_SetVtable(PyObject *dict, void *vtable); /*proto*/
static int __Pyx_GetVtable(PyObject *dict, void *vtabptr); /*proto*/
static PyObject *__Pyx_CreateClass(PyObject *bases, PyObject *dict, PyObject *name, char *modname); /*proto*/
static int __Pyx_InternStrings(__Pyx_InternTabEntry *t); /*proto*/
static int __Pyx_InitStrings(__Pyx_StringTabEntry *t); /*proto*/
static PyObject *__Pyx_GetName(PyObject *dict, PyObject *name); /*proto*/

static PyObject *__pyx_m;
static PyObject *__pyx_b;
static int __pyx_lineno;
static char *__pyx_filename;
staticforward char **__pyx_f;

static char __pyx_mdoc[] = "Wrapper for readdir which grabs file type from d_type.";

/* Declarations from readdir */


/* Implementation of readdir */

static char (__pyx_k11[]) = ".";

static PyObject *__pyx_n_os;
static PyObject *__pyx_n_sys;
static PyObject *__pyx_n__directory;
static PyObject *__pyx_n__chardev;
static PyObject *__pyx_n__block;
static PyObject *__pyx_n__file;
static PyObject *__pyx_n__fifo;
static PyObject *__pyx_n__symlink;
static PyObject *__pyx_n__socket;
static PyObject *__pyx_n__unknown;
static PyObject *__pyx_n_dot;
static PyObject *__pyx_n_read_dir;
static PyObject *__pyx_n_directory;
static PyObject *__pyx_n_chardev;
static PyObject *__pyx_n_block;
static PyObject *__pyx_n_file;
static PyObject *__pyx_n_fifo;
static PyObject *__pyx_n_symlink;
static PyObject *__pyx_n_socket;
static PyObject *__pyx_n_unknown;
static PyObject *__pyx_n_ord;

static PyObject *__pyx_k11p;

static PyObject *__pyx_n_append;
static PyObject *__pyx_n_OSError;

static PyObject *__pyx_f_7readdir_read_dir(PyObject *__pyx_self, PyObject *__pyx_args, PyObject *__pyx_kwds); /*proto*/
static char __pyx_doc_7readdir_read_dir[] = "Like os.listdir, this reads a directories contents.\n\n    :param path: the directory to list.\n    :return: a list of (basename, kind) tuples.\n    ";
static PyObject *__pyx_f_7readdir_read_dir(PyObject *__pyx_self, PyObject *__pyx_args, PyObject *__pyx_kwds) {
  PyObject *__pyx_v_path = 0;
  DIR (*__pyx_v_the_dir);
  dirent (*__pyx_v_entry);
  char (*__pyx_v_name);
  PyObject *__pyx_v_result;
  PyObject *__pyx_v_type;
  PyObject *__pyx_r;
  char (*__pyx_1);
  DIR (*__pyx_2);
  PyObject *__pyx_3 = 0;
  int __pyx_4;
  PyObject *__pyx_5 = 0;
  int __pyx_6;
  PyObject *__pyx_7 = 0;
  PyObject *__pyx_8 = 0;
  static char *__pyx_argnames[] = {"path",0};
  if (!PyArg_ParseTupleAndKeywords(__pyx_args, __pyx_kwds, "O", __pyx_argnames, &__pyx_v_path)) return 0;
  Py_INCREF(__pyx_v_path);
  __pyx_v_result = Py_None; Py_INCREF(__pyx_v_result);
  __pyx_v_type = Py_None; Py_INCREF(__pyx_v_type);

  /* "/home/robertc/source/baz/readdir/bzrlib/readdir.pyx":81 */
  __pyx_1 = PyString_AsString(__pyx_v_path); if (PyErr_Occurred()) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 81; goto __pyx_L1;}
  __pyx_2 = opendir(__pyx_1); if (__pyx_2 == 0) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 81; goto __pyx_L1;}
  __pyx_v_the_dir = __pyx_2;

  /* "/home/robertc/source/baz/readdir/bzrlib/readdir.pyx":82 */
  __pyx_3 = PyList_New(0); if (!__pyx_3) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 82; goto __pyx_L1;}
  Py_DECREF(__pyx_v_result);
  __pyx_v_result = __pyx_3;
  __pyx_3 = 0;

  /* "/home/robertc/source/baz/readdir/bzrlib/readdir.pyx":83 */
  /*try:*/ {

    /* "/home/robertc/source/baz/readdir/bzrlib/readdir.pyx":84 */
    __pyx_v_entry = readdir(__pyx_v_the_dir);

    /* "/home/robertc/source/baz/readdir/bzrlib/readdir.pyx":85 */
    while (1) {
      __pyx_L5:;
      __pyx_4 = (__pyx_v_entry != 0);
      if (!__pyx_4) break;

      /* "/home/robertc/source/baz/readdir/bzrlib/readdir.pyx":86 */
      __pyx_v_name = __pyx_v_entry->d_name;

      /* "/home/robertc/source/baz/readdir/bzrlib/readdir.pyx":87 */
      __pyx_3 = PyInt_FromLong((__pyx_v_name[0])); if (!__pyx_3) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 87; goto __pyx_L3;}
      __pyx_5 = __Pyx_GetName(__pyx_m, __pyx_n_dot); if (!__pyx_5) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 87; goto __pyx_L3;}
      if (PyObject_Cmp(__pyx_3, __pyx_5, &__pyx_4) < 0) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 87; goto __pyx_L3;}
      __pyx_4 = __pyx_4 == 0;
      Py_DECREF(__pyx_3); __pyx_3 = 0;
      Py_DECREF(__pyx_5); __pyx_5 = 0;
      if (__pyx_4) {
        __pyx_4 = ((__pyx_v_name[1]) == 0);
        if (!__pyx_4) {
          __pyx_3 = PyInt_FromLong((__pyx_v_name[1])); if (!__pyx_3) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 89; goto __pyx_L3;}
          __pyx_5 = __Pyx_GetName(__pyx_m, __pyx_n_dot); if (!__pyx_5) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 89; goto __pyx_L3;}
          if (PyObject_Cmp(__pyx_3, __pyx_5, &__pyx_4) < 0) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 89; goto __pyx_L3;}
          __pyx_4 = __pyx_4 == 0;
          Py_DECREF(__pyx_3); __pyx_3 = 0;
          Py_DECREF(__pyx_5); __pyx_5 = 0;
          if (__pyx_4) {
            __pyx_4 = ((__pyx_v_name[2]) == 0);
          }
        }
      }
      __pyx_6 = (!__pyx_4);
      if (__pyx_6) {

        /* "/home/robertc/source/baz/readdir/bzrlib/readdir.pyx":91 */
        __pyx_4 = (__pyx_v_entry->d_type == DT_UNKNOWN);
        if (__pyx_4) {

          /* "/home/robertc/source/baz/readdir/bzrlib/readdir.pyx":92 */
          __pyx_3 = __Pyx_GetName(__pyx_m, __pyx_n__unknown); if (!__pyx_3) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 92; goto __pyx_L3;}
          Py_DECREF(__pyx_v_type);
          __pyx_v_type = __pyx_3;
          __pyx_3 = 0;
          goto __pyx_L8;
        }
        __pyx_6 = (__pyx_v_entry->d_type == DT_REG);
        if (__pyx_6) {

          /* "/home/robertc/source/baz/readdir/bzrlib/readdir.pyx":94 */
          __pyx_5 = __Pyx_GetName(__pyx_m, __pyx_n__file); if (!__pyx_5) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 94; goto __pyx_L3;}
          Py_DECREF(__pyx_v_type);
          __pyx_v_type = __pyx_5;
          __pyx_5 = 0;
          goto __pyx_L8;
        }
        __pyx_4 = (__pyx_v_entry->d_type == DT_DIR);
        if (__pyx_4) {

          /* "/home/robertc/source/baz/readdir/bzrlib/readdir.pyx":96 */
          __pyx_3 = __Pyx_GetName(__pyx_m, __pyx_n__directory); if (!__pyx_3) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 96; goto __pyx_L3;}
          Py_DECREF(__pyx_v_type);
          __pyx_v_type = __pyx_3;
          __pyx_3 = 0;
          goto __pyx_L8;
        }
        __pyx_6 = (__pyx_v_entry->d_type == DT_FIFO);
        if (__pyx_6) {

          /* "/home/robertc/source/baz/readdir/bzrlib/readdir.pyx":98 */
          __pyx_5 = __Pyx_GetName(__pyx_m, __pyx_n__fifo); if (!__pyx_5) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 98; goto __pyx_L3;}
          Py_DECREF(__pyx_v_type);
          __pyx_v_type = __pyx_5;
          __pyx_5 = 0;
          goto __pyx_L8;
        }
        __pyx_4 = (__pyx_v_entry->d_type == DT_SOCK);
        if (__pyx_4) {

          /* "/home/robertc/source/baz/readdir/bzrlib/readdir.pyx":100 */
          __pyx_3 = __Pyx_GetName(__pyx_m, __pyx_n__socket); if (!__pyx_3) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 100; goto __pyx_L3;}
          Py_DECREF(__pyx_v_type);
          __pyx_v_type = __pyx_3;
          __pyx_3 = 0;
          goto __pyx_L8;
        }
        __pyx_6 = (__pyx_v_entry->d_type == DT_CHR);
        if (__pyx_6) {

          /* "/home/robertc/source/baz/readdir/bzrlib/readdir.pyx":102 */
          __pyx_5 = __Pyx_GetName(__pyx_m, __pyx_n__chardev); if (!__pyx_5) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 102; goto __pyx_L3;}
          Py_DECREF(__pyx_v_type);
          __pyx_v_type = __pyx_5;
          __pyx_5 = 0;
          goto __pyx_L8;
        }
        __pyx_4 = (__pyx_v_entry->d_type == DT_BLK);
        if (__pyx_4) {

          /* "/home/robertc/source/baz/readdir/bzrlib/readdir.pyx":104 */
          __pyx_3 = __Pyx_GetName(__pyx_m, __pyx_n__block); if (!__pyx_3) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 104; goto __pyx_L3;}
          Py_DECREF(__pyx_v_type);
          __pyx_v_type = __pyx_3;
          __pyx_3 = 0;
          goto __pyx_L8;
        }
        /*else*/ {

          /* "/home/robertc/source/baz/readdir/bzrlib/readdir.pyx":106 */
          __pyx_5 = __Pyx_GetName(__pyx_m, __pyx_n__unknown); if (!__pyx_5) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 106; goto __pyx_L3;}
          Py_DECREF(__pyx_v_type);
          __pyx_v_type = __pyx_5;
          __pyx_5 = 0;
        }
        __pyx_L8:;

        /* "/home/robertc/source/baz/readdir/bzrlib/readdir.pyx":107 */
        __pyx_3 = PyObject_GetAttr(__pyx_v_result, __pyx_n_append); if (!__pyx_3) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 107; goto __pyx_L3;}
        __pyx_5 = PyString_FromString(__pyx_v_entry->d_name); if (!__pyx_5) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 107; goto __pyx_L3;}
        __pyx_7 = PyTuple_New(2); if (!__pyx_7) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 107; goto __pyx_L3;}
        PyTuple_SET_ITEM(__pyx_7, 0, __pyx_5);
        Py_INCREF(__pyx_v_type);
        PyTuple_SET_ITEM(__pyx_7, 1, __pyx_v_type);
        __pyx_5 = 0;
        __pyx_5 = PyTuple_New(1); if (!__pyx_5) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 107; goto __pyx_L3;}
        PyTuple_SET_ITEM(__pyx_5, 0, __pyx_7);
        __pyx_7 = 0;
        __pyx_7 = PyObject_CallObject(__pyx_3, __pyx_5); if (!__pyx_7) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 107; goto __pyx_L3;}
        Py_DECREF(__pyx_3); __pyx_3 = 0;
        Py_DECREF(__pyx_5); __pyx_5 = 0;
        Py_DECREF(__pyx_7); __pyx_7 = 0;
        goto __pyx_L7;
      }
      __pyx_L7:;

      /* "/home/robertc/source/baz/readdir/bzrlib/readdir.pyx":108 */
      __pyx_v_entry = readdir(__pyx_v_the_dir);
    }
    __pyx_L6:;

    /* "/home/robertc/source/baz/readdir/bzrlib/readdir.pyx":109 */
    __pyx_6 = (__pyx_v_entry == 0);
    if (__pyx_6) {
      __pyx_6 = (errno != ENOENT);
      if (__pyx_6) {
        __pyx_6 = (errno != 0);
      }
    }
    if (__pyx_6) {

      /* "/home/robertc/source/baz/readdir/bzrlib/readdir.pyx":110 */
      __pyx_3 = __Pyx_GetName(__pyx_b, __pyx_n_OSError); if (!__pyx_3) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 110; goto __pyx_L3;}
      __pyx_5 = PyInt_FromLong(errno); if (!__pyx_5) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 110; goto __pyx_L3;}
      __pyx_7 = PyString_FromString(strerror(errno)); if (!__pyx_7) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 110; goto __pyx_L3;}
      __pyx_8 = PyTuple_New(2); if (!__pyx_8) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 110; goto __pyx_L3;}
      PyTuple_SET_ITEM(__pyx_8, 0, __pyx_5);
      PyTuple_SET_ITEM(__pyx_8, 1, __pyx_7);
      __pyx_5 = 0;
      __pyx_7 = 0;
      __pyx_5 = PyObject_CallObject(__pyx_3, __pyx_8); if (!__pyx_5) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 110; goto __pyx_L3;}
      Py_DECREF(__pyx_3); __pyx_3 = 0;
      Py_DECREF(__pyx_8); __pyx_8 = 0;
      __Pyx_Raise(__pyx_5, 0, 0);
      Py_DECREF(__pyx_5); __pyx_5 = 0;
      {__pyx_filename = __pyx_f[0]; __pyx_lineno = 110; goto __pyx_L3;}
      goto __pyx_L9;
    }
    __pyx_L9:;
  }
  /*finally:*/ {
    int __pyx_why;
    __pyx_why = 0; goto __pyx_L4;
    __pyx_L2: __pyx_why = 3; goto __pyx_L4;
    __pyx_L3: {
      __pyx_why = 4;
      Py_XDECREF(__pyx_7); __pyx_7 = 0;
      Py_XDECREF(__pyx_3); __pyx_3 = 0;
      Py_XDECREF(__pyx_8); __pyx_8 = 0;
      Py_XDECREF(__pyx_5); __pyx_5 = 0;
      PyErr_Fetch(&__pyx_7, &__pyx_3, &__pyx_8);
      __pyx_4 = __pyx_lineno;
      goto __pyx_L4;
    }
    __pyx_L4:;

    /* "/home/robertc/source/baz/readdir/bzrlib/readdir.pyx":112 */
    __pyx_6 = closedir(__pyx_v_the_dir); if (__pyx_6 == -1) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 112; goto __pyx_L1;}
    switch (__pyx_why) {
      case 3: goto __pyx_L0;
      case 4: {
        PyErr_Restore(__pyx_7, __pyx_3, __pyx_8);
        __pyx_lineno = __pyx_4;
        __pyx_7 = 0;
        __pyx_3 = 0;
        __pyx_8 = 0;
        goto __pyx_L1;
      }
    }
  }

  /* "/home/robertc/source/baz/readdir/bzrlib/readdir.pyx":113 */
  Py_INCREF(__pyx_v_result);
  __pyx_r = __pyx_v_result;
  goto __pyx_L0;

  __pyx_r = Py_None; Py_INCREF(__pyx_r);
  goto __pyx_L0;
  __pyx_L1:;
  Py_XDECREF(__pyx_3);
  Py_XDECREF(__pyx_5);
  Py_XDECREF(__pyx_7);
  Py_XDECREF(__pyx_8);
  __Pyx_AddTraceback("readdir.read_dir");
  __pyx_r = 0;
  __pyx_L0:;
  Py_DECREF(__pyx_v_result);
  Py_DECREF(__pyx_v_type);
  Py_DECREF(__pyx_v_path);
  return __pyx_r;
}

static __Pyx_InternTabEntry __pyx_intern_tab[] = {
  {&__pyx_n_OSError, "OSError"},
  {&__pyx_n__block, "_block"},
  {&__pyx_n__chardev, "_chardev"},
  {&__pyx_n__directory, "_directory"},
  {&__pyx_n__fifo, "_fifo"},
  {&__pyx_n__file, "_file"},
  {&__pyx_n__socket, "_socket"},
  {&__pyx_n__symlink, "_symlink"},
  {&__pyx_n__unknown, "_unknown"},
  {&__pyx_n_append, "append"},
  {&__pyx_n_block, "block"},
  {&__pyx_n_chardev, "chardev"},
  {&__pyx_n_directory, "directory"},
  {&__pyx_n_dot, "dot"},
  {&__pyx_n_fifo, "fifo"},
  {&__pyx_n_file, "file"},
  {&__pyx_n_ord, "ord"},
  {&__pyx_n_os, "os"},
  {&__pyx_n_read_dir, "read_dir"},
  {&__pyx_n_socket, "socket"},
  {&__pyx_n_symlink, "symlink"},
  {&__pyx_n_sys, "sys"},
  {&__pyx_n_unknown, "unknown"},
  {0, 0}
};

static __Pyx_StringTabEntry __pyx_string_tab[] = {
  {&__pyx_k11p, __pyx_k11, sizeof(__pyx_k11)},
  {0, 0, 0}
};

static struct PyMethodDef __pyx_methods[] = {
  {"read_dir", (PyCFunction)__pyx_f_7readdir_read_dir, METH_VARARGS|METH_KEYWORDS, __pyx_doc_7readdir_read_dir},
  {0, 0, 0, 0}
};

DL_EXPORT(void) initreaddir(void); /*proto*/
DL_EXPORT(void) initreaddir(void) {
  PyObject *__pyx_1 = 0;
  PyObject *__pyx_2 = 0;
  PyObject *__pyx_3 = 0;
  __pyx_m = Py_InitModule4("readdir", __pyx_methods, __pyx_mdoc, 0, PYTHON_API_VERSION);
  if (!__pyx_m) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 19; goto __pyx_L1;};
  __pyx_b = PyImport_AddModule("__builtin__");
  if (!__pyx_b) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 19; goto __pyx_L1;};
  if (PyObject_SetAttrString(__pyx_m, "__builtins__", __pyx_b) < 0) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 19; goto __pyx_L1;};
  if (__Pyx_InternStrings(__pyx_intern_tab) < 0) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 19; goto __pyx_L1;};
  if (__Pyx_InitStrings(__pyx_string_tab) < 0) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 19; goto __pyx_L1;};

  /* "/home/robertc/source/baz/readdir/bzrlib/readdir.pyx":22 */
  __pyx_1 = __Pyx_Import(__pyx_n_os, 0); if (!__pyx_1) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 22; goto __pyx_L1;}
  if (PyObject_SetAttr(__pyx_m, __pyx_n_os, __pyx_1) < 0) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 22; goto __pyx_L1;}
  Py_DECREF(__pyx_1); __pyx_1 = 0;

  /* "/home/robertc/source/baz/readdir/bzrlib/readdir.pyx":23 */
  __pyx_1 = __Pyx_Import(__pyx_n_sys, 0); if (!__pyx_1) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 23; goto __pyx_L1;}
  if (PyObject_SetAttr(__pyx_m, __pyx_n_sys, __pyx_1) < 0) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 23; goto __pyx_L1;}
  Py_DECREF(__pyx_1); __pyx_1 = 0;

  /* "/home/robertc/source/baz/readdir/bzrlib/readdir.pyx":55 */
  if (PyObject_SetAttr(__pyx_m, __pyx_n__directory, __pyx_n_directory) < 0) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 55; goto __pyx_L1;}

  /* "/home/robertc/source/baz/readdir/bzrlib/readdir.pyx":56 */
  if (PyObject_SetAttr(__pyx_m, __pyx_n__chardev, __pyx_n_chardev) < 0) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 56; goto __pyx_L1;}

  /* "/home/robertc/source/baz/readdir/bzrlib/readdir.pyx":57 */
  if (PyObject_SetAttr(__pyx_m, __pyx_n__block, __pyx_n_block) < 0) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 57; goto __pyx_L1;}

  /* "/home/robertc/source/baz/readdir/bzrlib/readdir.pyx":58 */
  if (PyObject_SetAttr(__pyx_m, __pyx_n__file, __pyx_n_file) < 0) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 58; goto __pyx_L1;}

  /* "/home/robertc/source/baz/readdir/bzrlib/readdir.pyx":59 */
  if (PyObject_SetAttr(__pyx_m, __pyx_n__fifo, __pyx_n_fifo) < 0) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 59; goto __pyx_L1;}

  /* "/home/robertc/source/baz/readdir/bzrlib/readdir.pyx":60 */
  if (PyObject_SetAttr(__pyx_m, __pyx_n__symlink, __pyx_n_symlink) < 0) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 60; goto __pyx_L1;}

  /* "/home/robertc/source/baz/readdir/bzrlib/readdir.pyx":61 */
  if (PyObject_SetAttr(__pyx_m, __pyx_n__socket, __pyx_n_socket) < 0) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 61; goto __pyx_L1;}

  /* "/home/robertc/source/baz/readdir/bzrlib/readdir.pyx":62 */
  if (PyObject_SetAttr(__pyx_m, __pyx_n__unknown, __pyx_n_unknown) < 0) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 62; goto __pyx_L1;}

  /* "/home/robertc/source/baz/readdir/bzrlib/readdir.pyx":64 */
  __pyx_1 = __Pyx_GetName(__pyx_b, __pyx_n_ord); if (!__pyx_1) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 64; goto __pyx_L1;}
  __pyx_2 = PyTuple_New(1); if (!__pyx_2) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 64; goto __pyx_L1;}
  Py_INCREF(__pyx_k11p);
  PyTuple_SET_ITEM(__pyx_2, 0, __pyx_k11p);
  __pyx_3 = PyObject_CallObject(__pyx_1, __pyx_2); if (!__pyx_3) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 64; goto __pyx_L1;}
  Py_DECREF(__pyx_1); __pyx_1 = 0;
  Py_DECREF(__pyx_2); __pyx_2 = 0;
  if (PyObject_SetAttr(__pyx_m, __pyx_n_dot, __pyx_3) < 0) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 64; goto __pyx_L1;}
  Py_DECREF(__pyx_3); __pyx_3 = 0;

  /* "/home/robertc/source/baz/readdir/bzrlib/readdir.pyx":70 */
  return;
  __pyx_L1:;
  Py_XDECREF(__pyx_1);
  Py_XDECREF(__pyx_2);
  Py_XDECREF(__pyx_3);
  __Pyx_AddTraceback("readdir");
}

static char *__pyx_filenames[] = {
  "readdir.pyx",
};
statichere char **__pyx_f = __pyx_filenames;

/* Runtime support code */

static PyObject *__Pyx_Import(PyObject *name, PyObject *from_list) {
    PyObject *__import__ = 0;
    PyObject *empty_list = 0;
    PyObject *module = 0;
    PyObject *global_dict = 0;
    PyObject *empty_dict = 0;
    PyObject *list;
    __import__ = PyObject_GetAttrString(__pyx_b, "__import__");
    if (!__import__)
        goto bad;
    if (from_list)
        list = from_list;
    else {
        empty_list = PyList_New(0);
        if (!empty_list)
            goto bad;
        list = empty_list;
    }
    global_dict = PyModule_GetDict(__pyx_m);
    if (!global_dict)
        goto bad;
    empty_dict = PyDict_New();
    if (!empty_dict)
        goto bad;
    module = PyObject_CallFunction(__import__, "OOOO",
        name, global_dict, empty_dict, list);
bad:
    Py_XDECREF(empty_list);
    Py_XDECREF(__import__);
    Py_XDECREF(empty_dict);
    return module;
}

static PyObject *__Pyx_GetName(PyObject *dict, PyObject *name) {
    PyObject *result;
    result = PyObject_GetAttr(dict, name);
    if (!result)
        PyErr_SetObject(PyExc_NameError, name);
    return result;
}

static void __Pyx_Raise(PyObject *type, PyObject *value, PyObject *tb) {
    Py_XINCREF(type);
    Py_XINCREF(value);
    Py_XINCREF(tb);
    /* First, check the traceback argument, replacing None with NULL. */
    if (tb == Py_None) {
        Py_DECREF(tb);
        tb = 0;
    }
    else if (tb != NULL && !PyTraceBack_Check(tb)) {
        PyErr_SetString(PyExc_TypeError,
            "raise: arg 3 must be a traceback or None");
        goto raise_error;
    }
    /* Next, replace a missing value with None */
    if (value == NULL) {
        value = Py_None;
        Py_INCREF(value);
    }
    /* Next, repeatedly, replace a tuple exception with its first item */
    while (PyTuple_Check(type) && PyTuple_Size(type) > 0) {
        PyObject *tmp = type;
        type = PyTuple_GET_ITEM(type, 0);
        Py_INCREF(type);
        Py_DECREF(tmp);
    }
    if (PyString_Check(type))
        ;
    else if (PyClass_Check(type))
        ; /*PyErr_NormalizeException(&type, &value, &tb);*/
    else if (PyInstance_Check(type)) {
        /* Raising an instance.  The value should be a dummy. */
        if (value != Py_None) {
            PyErr_SetString(PyExc_TypeError,
              "instance exception may not have a separate value");
            goto raise_error;
        }
        else {
            /* Normalize to raise <class>, <instance> */
            Py_DECREF(value);
            value = type;
            type = (PyObject*) ((PyInstanceObject*)type)->in_class;
            Py_INCREF(type);
        }
    }
    else {
        /* Not something you can raise.  You get an exception
           anyway, just not what you specified :-) */
        PyErr_Format(PyExc_TypeError,
                 "exceptions must be strings, classes, or "
                 "instances, not %s", type->ob_type->tp_name);
        goto raise_error;
    }
    PyErr_Restore(type, value, tb);
    return;
raise_error:
    Py_XDECREF(value);
    Py_XDECREF(type);
    Py_XDECREF(tb);
    return;
}

static int __Pyx_InternStrings(__Pyx_InternTabEntry *t) {
    while (t->p) {
        *t->p = PyString_InternFromString(t->s);
        if (!*t->p)
            return -1;
        ++t;
    }
    return 0;
}

static int __Pyx_InitStrings(__Pyx_StringTabEntry *t) {
    while (t->p) {
        *t->p = PyString_FromStringAndSize(t->s, t->n - 1);
        if (!*t->p)
            return -1;
        ++t;
    }
    return 0;
}

#include "compile.h"
#include "frameobject.h"
#include "traceback.h"

static void __Pyx_AddTraceback(char *funcname) {
    PyObject *py_srcfile = 0;
    PyObject *py_funcname = 0;
    PyObject *py_globals = 0;
    PyObject *empty_tuple = 0;
    PyObject *empty_string = 0;
    PyCodeObject *py_code = 0;
    PyFrameObject *py_frame = 0;
    
    py_srcfile = PyString_FromString(__pyx_filename);
    if (!py_srcfile) goto bad;
    py_funcname = PyString_FromString(funcname);
    if (!py_funcname) goto bad;
    py_globals = PyModule_GetDict(__pyx_m);
    if (!py_globals) goto bad;
    empty_tuple = PyTuple_New(0);
    if (!empty_tuple) goto bad;
    empty_string = PyString_FromString("");
    if (!empty_string) goto bad;
    py_code = PyCode_New(
        0,            /*int argcount,*/
        0,            /*int nlocals,*/
        0,            /*int stacksize,*/
        0,            /*int flags,*/
        empty_string, /*PyObject *code,*/
        empty_tuple,  /*PyObject *consts,*/
        empty_tuple,  /*PyObject *names,*/
        empty_tuple,  /*PyObject *varnames,*/
        empty_tuple,  /*PyObject *freevars,*/
        empty_tuple,  /*PyObject *cellvars,*/
        py_srcfile,   /*PyObject *filename,*/
        py_funcname,  /*PyObject *name,*/
        __pyx_lineno,   /*int firstlineno,*/
        empty_string  /*PyObject *lnotab*/
    );
    if (!py_code) goto bad;
    py_frame = PyFrame_New(
        PyThreadState_Get(), /*PyThreadState *tstate,*/
        py_code,             /*PyCodeObject *code,*/
        py_globals,          /*PyObject *globals,*/
        0                    /*PyObject *locals*/
    );
    if (!py_frame) goto bad;
    py_frame->f_lineno = __pyx_lineno;
    PyTraceBack_Here(py_frame);
bad:
    Py_XDECREF(py_srcfile);
    Py_XDECREF(py_funcname);
    Py_XDECREF(empty_tuple);
    Py_XDECREF(empty_string);
    Py_XDECREF(py_code);
    Py_XDECREF(py_frame);
}
