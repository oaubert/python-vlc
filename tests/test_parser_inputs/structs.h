// ============================================================================
// Regular structs
// ============================================================================
struct not_from_libvlc_struct {
  int a;
  char b;
  double c;
};

struct libvlc_struct_no_values_specified {
  int a;
  char b;
  double c;
};

struct libvlc_struct_all_values_specified {
  int a = 1;
  char b = 'b';
  double c = 1.1;
};

/** Some Doxygen
 * documentation
 * that spans
 * multiple lines
 */
struct libvlc_struct_with_docs {
  int a = 2;
  char b = 'c';
  double c = 1.2;
};

// To test constness
struct libvlc_struct_with_const {
  const char x;
};

// To test pointers and pointers with constness
struct libvlc_struct_pointers {
  const int *x;
  double *const y;
};

struct libvlc_struct_with_anonymous_nested_union {
  int a;
  union {
    char b;
    char c;
  };
  double d;
};

struct libvlc_struct_with_named_nested_union {
  int a;
  union {
    char b;
    char c;
  } u;
  double d;
};

struct libvlc_struct_with_anonymous_nested_struct {
  int a;
  struct {
    char b;
    char c;
  };
  double d;
};

struct libvlc_struct_with_named_nested_struct {
  int a;
  struct {
    char b;
    char c;
  } s;
  double d;
};

struct libvlc_struct_with_nested_anonymous_union_and_struct {
  int a;
  union {
    char b;
  };
  struct {
    char c;
  };
  double d;
};

struct libvlc_struct_with_nested_named_union_and_struct {
  int a;
  union {
    char b;
  } u;
  struct {
    char c;
  } s;
  double d;
};

struct libvlc_struct_with_nested_anonymous_union_and_nested_struct_inside {
  int a;
  union {
    char b;
    struct {
      char c;
    };
    struct {
      char d;
    };
  };
  double e;
};

struct libvlc_struct_with_nested_named_union_and_nested_struct_inside {
  int a;
  union {
    char b;
    struct {
      char c;
    } s1;
    struct {
      char d;
    } s2;
  } u;
  double e;
};

struct libvlc_struct_with_callbacks {
  /**
   * Some docs for cb1.
   */
  void (*cb1)();
  /**
   * Some docs for cb2.
   */
  void (*cb2)();
  /**
   * Some docs for cb3.
   */
  void (*cb3)();
};

struct libvlc_struct_with_complex_callbacks {
  char *(*cb1)(int a, double b);
  char **(*cb2)(int a, double b);
  char ***(*cb3)(int a, double b);
};

struct libvlc_struct_with_cb_taking_cb_as_argument {
  char *(*cb)(int (*cb_param)(int a, double b, char c));
};

// ============================================================================
// Typedef structs
// ============================================================================
typedef struct not_from_libvlc_struct_t {
  int a;
  char b;
  double c;
} not_from_libvlc_struct_t;

typedef struct libvlc_struct_no_values_specified_t {
  int a;
  char b;
  double c;
} libvlc_struct_no_values_specified_t;

typedef struct libvlc_struct_all_values_specified_t {
  int a = 1;
  char b = 'b';
  double c = 1.1;
} libvlc_struct_all_values_specified_t;

/** Some Doxygen
 * documentation
 * that spans
 * multiple lines
 */
typedef struct libvlc_struct_with_docs_t {
  int a = 2;
  char b = 'c';
  double c = 1.2;
} libvlc_struct_with_docs_t;

// To test that the name taken into account
// is the typedef's name, not the struct's name.
typedef struct libvlc_struct {
  char x;
} libvlc_struct_t;

// To test constness
typedef struct libvlc_struct_with_const_t {
  const char x;
} libvlc_struct_with_const_t;

// To test pointers and pointers with constness
typedef struct libvlc_struct_pointers_t {
  const int *x;
  double *const y;
} libvlc_struct_pointers_t;

typedef struct libvlc_struct_with_anonymous_nested_union_t {
  int a;
  union {
    char b;
    char c;
  };
  double d;
} libvlc_struct_with_anonymous_nested_union_t;

typedef struct libvlc_struct_with_named_nested_union_t {
  int a;
  union {
    char b;
    char c;
  } u;
  double d;
} libvlc_struct_with_named_nested_union_t;

typedef struct libvlc_struct_with_anonymous_nested_struct_t {
  int a;
  struct {
    char b;
    char c;
  };
  double d;
} libvlc_struct_with_anonymous_nested_struct_t;

typedef struct libvlc_struct_with_named_nested_struct_t {
  int a;
  struct {
    char b;
    char c;
  } s;
  double d;
} libvlc_struct_with_named_nested_struct_t;

typedef struct libvlc_struct_with_nested_anonymous_union_and_struct_t {
  int a;
  union {
    char b;
  };
  struct {
    char c;
  };
  double d;
} libvlc_struct_with_nested_anonymous_union_and_struct_t;

typedef struct libvlc_struct_with_nested_named_union_and_struct_t {
  int a;
  union {
    char b;
  } u;
  struct {
    char c;
  } s;
  double d;
} libvlc_struct_with_nested_named_union_and_struct_t;

typedef struct
    libvlc_struct_with_nested_anonymous_union_and_nested_struct_inside_t {
  int a;
  union {
    char b;
    struct {
      char c;
    };
    struct {
      char d;
    };
  };
  double e;
} libvlc_struct_with_nested_anonymous_union_and_nested_struct_inside_t;

typedef struct
    libvlc_struct_with_nested_named_union_and_nested_struct_inside_t {
  int a;
  union {
    char b;
    struct {
      char c;
    } s1;
    struct {
      char d;
    } s2;
  } u;
  double e;
} libvlc_struct_with_nested_named_union_and_nested_struct_inside_t;

typedef struct libvlc_struct_with_callbacks_t {
  /**
   * Some docs for cb1.
   */
  void (*cb1)();
  /**
   * Some docs for cb2.
   */
  void (*cb2)();
  /**
   * Some docs for cb3.
   */
  void (*cb3)();
} libvlc_struct_with_callbacks_t;

typedef struct libvlc_struct_with_complex_callbacks_t {
  char *(*cb1)(int a, double b);
  char **(*cb2)(int a, double b);
  char ***(*cb3)(int a, double b);
} libvlc_struct_with_complex_callbacks_t;

typedef struct libvlc_struct_with_cb_taking_cb_as_argument_t {
  char *(*cb)(int (*cb_param)(int a, double b, char c));
} libvlc_struct_with_cb_taking_cb_as_argument_t;
