import collections, glob
def varint(b, i):
    r = s = 0
    while True:
        c = b[i]; i += 1; r |= (c & 0x7f) << s; s += 7
        if c < 0x80: return r, i
def layers(b):
    i = 0; out = []
    while i < len(b):
        key, i = varint(b, i); ln, j = varint(b, i)
        start, end = i, j + ln
        if key >> 3 == 3:
            body = b[j:end]; k, p = varint(body, 0); nl, p = varint(body, p)
            out.append((body[p:p+nl].decode(), start, end))
        i = end
    return out
if __name__ == "__main__":
    c = collections.Counter()
    for f in glob.glob("tcache/*"):
        b = open(f, "rb").read()
        for n, s, e in layers(b): c[n] += e - s
    for n, v in c.most_common(): print(f"{n:22s} {v/1e6:.2f} MB")
