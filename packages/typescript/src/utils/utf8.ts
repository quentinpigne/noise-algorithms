/**
 * Encode a string to its UTF-8 bytes, without relying on `TextEncoder`, so the
 * library stays environment-agnostic (no DOM/Node lib required). Produces the
 * same bytes as Python's `str.encode("utf-8")`.
 */
export function utf8Bytes(text: string): number[] {
  const bytes: number[] = [];

  for (let i = 0; i < text.length; i++) {
    let cp = text.charCodeAt(i);
    // Combine a UTF-16 surrogate pair into a single code point.
    if (cp >= 0xd800 && cp <= 0xdbff && i + 1 < text.length) {
      const low = text.charCodeAt(i + 1);
      if (low >= 0xdc00 && low <= 0xdfff) {
        cp = 0x10000 + ((cp - 0xd800) << 10) + (low - 0xdc00);
        i++;
      }
    }

    if (cp < 0x80) {
      bytes.push(cp);
    } else if (cp < 0x800) {
      bytes.push(0xc0 | (cp >> 6), 0x80 | (cp & 0x3f));
    } else if (cp < 0x10000) {
      bytes.push(
        0xe0 | (cp >> 12),
        0x80 | ((cp >> 6) & 0x3f),
        0x80 | (cp & 0x3f),
      );
    } else {
      bytes.push(
        0xf0 | (cp >> 18),
        0x80 | ((cp >> 12) & 0x3f),
        0x80 | ((cp >> 6) & 0x3f),
        0x80 | (cp & 0x3f),
      );
    }
  }

  return bytes;
}
