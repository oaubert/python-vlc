void libvlc_not_in_public_api();

__attribute__((visibility("default"))) void not_a_libvlc_function();

__attribute__((visibility("default"))) void libvlc_simple();

__attribute__((visibility("default"))) void libvlc_simple_with_void(void);

__attribute__((visibility("default")))
void libvlc_attribute_on_the_previous_line();

/** Some Doxygen
 * documentation
 * that spans
 * multiple lines
 */
__attribute__((visibility("default"))) void libvlc_with_docs();

__attribute__((visibility("default"))) char libvlc_simple_types(int a, float b);

__attribute__((visibility("default"))) char* libvlc_pointer_as_return_type(int a, float b);

__attribute__((visibility("default"))) const char* libvlc_pointer_as_return_type_with_qualifier(int a, float b);

__attribute__((visibility("default"))) const char* libvlc_pointers_and_qualifiers_everywhere(const char* c1, const char* c2);

__attribute__((visibility("default"))) const char** libvlc_multiple_pointers(char** c1, char*** c2);

__attribute__((visibility("default"))) const char* const* libvlc_multiple_pointers_and_qualifiers(const char** const c1, char* const* const* const c2);

__attribute__((visibility("default"))) void libvlc_function_pointer_as_param(void (*cb)());

__attribute__((visibility("default"))) void libvlc_complex_function_pointer_as_param(const char* (*cb)(char* const* const*));

__attribute__((visibility("default"))) void libvlc_complex_function_pointer_as_param_with_named_params(char** (*cb)(char* const* const* c1, char* const* * c2), int i, double d);
