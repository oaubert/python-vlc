// ============================================================================
// Regular enums
// ============================================================================
enum not_from_libvlc_enum { A, B, C };

// Anonymous enum
enum { D, E, F };

enum libvlc_enum_no_values_specified { G, H, I };

enum libvlc_enum_all_values_specified { J = 2, K = 4, L = 6 };

enum libvlc_enum_values_specified_or_not {
  M = 5,
  N, // Expect 6
  O = 8,
  P // Expect 9
};

/** Some Doxygen
 * documentation
 * that spans
 * multiple lines
 */
enum libvlc_enum_with_docs {
  Q = 5,
  R, // Expect 6
  S = 8,
  T // Expect 9
};

enum libvlc_enum_with_hex_values { U = 0x1, V = 0xf };

enum libvlc_enum_with_bit_shifted_values { W = 'r' << 16, X = 'g' << 16 };

enum libvlc_enum_with_deprecated_values {
  A1 __attribute__((deprecated)) = 1,
  A2 __attribute__((deprecated))
};

// ============================================================================
// Typedef enums
// ============================================================================
typedef enum not_from_libvlc_enum_t { AA, BB, CC } not_from_libvlc_enum_t;

typedef enum libvlc_enum_no_values_specified_t {
  GG,
  HH,
  II
} libvlc_enum_no_values_specified_t;

typedef enum libvlc_enum_all_values_specified_t {
  JJ = 2,
  KK = 4,
  LL = 6
} libvlc_enum_all_values_specified_t;

typedef enum libvlc_enum_values_specified_or_not_t {
  MM = 5,
  NN, // Expect 6
  OO = 8,
  PP // Expect 9
} libvlc_enum_values_specified_or_not_t;

/** Some Doxygen
 * documentation
 * that spans
 * multiple lines
 */
typedef enum libvlc_enum_with_docs_t {
  QQ = 5,
  RR, // Expect 6
  SS = 8,
  TT // Expect 9
} libvlc_enum_with_docs_t;

typedef enum libvlc_enum_with_hex_values_t {
  UU = 0x1,
  VV = 0xf
} libvlc_enum_with_hex_values_t;

typedef enum libvlc_enum_with_bit_shifted_values_t {
  WW = 'r' << 16,
  XX = 'g' << 16
} libvlc_enum_with_bit_shifted_values_t;

// To test that the name taken into account
// is the typedef's name, not the enum's name.
typedef enum libvlc_enum { ZZ } libvlc_enum_t;

typedef enum libvlc_enum_with_deprecated_values_t {
  AA1 __attribute__((deprecated)) = 1,
  AA2 __attribute__((deprecated))
} libvlc_enum_with_deprecated_values_t;
