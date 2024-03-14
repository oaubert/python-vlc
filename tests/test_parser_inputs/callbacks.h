typedef void (*not_in_libvlc_cb)();

typedef void (*libvlc_simple_cb)();

typedef void (*libvlc_simple_with_void_cb)(void);

typedef void* (*libvlc_simple_with_void_pointers_cb)(void* p);

typedef char (*libvlc_simple_types_cb)(int a, float b);

/** Some Doxygen
 * documentation
 * that spans
 * multiple lines
 */
typedef char (*libvlc_with_docs_cb)(int a, float b);

typedef char* (*libvlc_one_pointer_cb)(char* c1, char* c2, char* c3);

typedef const char* (*libvlc_one_pointer_and_const_cb)(const char* c1, char* c2, char* c3);

typedef char** (*libvlc_multiple_pointers_cb)(char** c1, char*** c2, char**** c3);

typedef const char** (*libvlc_multiple_pointers_with_const_cb)(const char* const* c1, char* const* const* const c2, char* const** const* c3);

// // TODO: Change parse_callbacks_with_ts to handle the following cases (function pointer as parameter and/or return type)
//
// // typedef void (*libvlc_function_pointer_as_param_cb)(void (*cb)());
// //
// // typedef void (*libvlc_complex_function_pointer_as_param_cb)(const char* (*cb)(char* const* const*));
// //
// // typedef bool (*libvlc_function_pointer_as_return_type_cb(int a, float b))(bool b, char c);
