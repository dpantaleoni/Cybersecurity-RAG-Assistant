# NCL Cryptography Basics

## Overview

Cryptography challenges in the National Cyber League (NCL) test your understanding of encryption, decryption, hashing, and encoding techniques.

## Common Cryptography Techniques

### 1. Caesar Cipher

The Caesar cipher is a simple substitution cipher where each letter is shifted by a fixed number of positions.

**Example:**
- Plaintext: HELLO
- Shift: 3
- Ciphertext: KHOOR

**Tools:**
- CyberChef
- Python `str.translate()`
- Online Caesar cipher decoders

### 2. Base64 Encoding

Base64 is not encryption but encoding. It's commonly used to encode binary data as ASCII text.

**Identification:**
- Ends with `=` or `==` padding
- Uses characters A-Z, a-z, 0-9, +, /

**Decoding:**
```bash
echo "SGVsbG8gV29ybGQ=" | base64 -d
```

### 3. ROT13

ROT13 is a special case of Caesar cipher with a shift of 13.

**Example:**
- Plaintext: HELLO
- Ciphertext: URYYB

### 4. RSA Encryption

RSA is an asymmetric encryption algorithm using public and private keys.

**Key Concepts:**
- Public key (n, e) for encryption
- Private key (n, d) for decryption
- Based on difficulty of factoring large numbers

**Common NCL RSA Challenges:**
- Small exponent attack (e=3)
- Small modulus factorization
- Common modulus attack
- Wiener's attack for small d

**Tools:**
- RsaCtfTool
- OpenSSL
- Python `pycryptodome` library

### 5. XOR Encryption

XOR is a simple but powerful encryption technique.

**Properties:**
- A ⊕ B ⊕ B = A
- Reversible with the same key
- Used in stream ciphers

**Breaking XOR:**
- Single-byte XOR: Brute force 256 keys
- Multi-byte XOR: Frequency analysis
- Known plaintext attack

### 6. Hash Functions

Hash functions create fixed-size outputs from variable-size inputs.

**Common Hashes:**
- MD5: 32 hex characters (weak, avoid for security)
- SHA-1: 40 hex characters (deprecated)
- SHA-256: 64 hex characters (recommended)
- SHA-512: 128 hex characters

**Hash Cracking:**
- Rainbow tables
- Hashcat
- John the Ripper
- Online databases (CrackStation, HashKiller)

### 7. Substitution Ciphers

Each letter is replaced with another letter or symbol.

**Breaking Techniques:**
- Frequency analysis
- Pattern recognition
- Known plaintext

## NCL Tips

1. **Recognize the encoding/encryption type first**
   - Look for patterns (=, padding, character sets)
   - Check length and format
   - Try common tools like CyberChef

2. **Use CyberChef**
   - Great for chaining operations
   - Auto-detect features
   - URL: https://gchq.github.io/CyberChef/

3. **Keep a toolkit ready**
   - Python with pycryptodome
   - OpenSSL
   - Hashcat
   - John the Ripper
   - RsaCtfTool

4. **Common CTF crypto patterns**
   - Multiple layers of encoding
   - Combination of techniques
   - Hidden messages in ciphertext
   - Steganography combined with crypto

## Practice Resources

- CryptoHack (https://cryptohack.org/)
- OverTheWire Krypton
- PicoCTF crypto challenges
- CryptoPals challenges

## Common Commands

```bash
# Base64
echo "text" | base64
echo "encoded" | base64 -d

# MD5 hash
echo -n "password" | md5sum

# SHA-256 hash
echo -n "password" | sha256sum

# OpenSSL RSA
openssl rsa -in private.pem -text -noout
openssl rsautl -decrypt -inkey private.pem -in encrypted.txt

# Hashcat
hashcat -m 0 hash.txt wordlist.txt  # MD5
hashcat -m 1000 hash.txt wordlist.txt  # NTLM
```

## Red Flags in NCL

- "The flag is encrypted" → Usually multiple steps
- Large numbers in text → Possible RSA
- Random-looking base64 → Could be encrypted data
- Repeating patterns → Substitution or Vigenère
- Short ciphertext → Possible classical cipher

Remember: Most NCL crypto challenges are solvable with common tools and techniques. Don't overthink it!

