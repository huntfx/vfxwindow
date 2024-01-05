import re


def standardiseVersions(a, b):
    """Take two versions and return their standardised values.
    These should only be used for comparison operations, as the return
    types are varied and the implementation may be subject to change.

    Note that varied version separators such as `1.5v2` are treated like
    `1.5.2` for the sake of simplicity.

    Returns:
        Tuple of 2 values of varying types.

    Tests:
        >>> standardiseVersions('1.2.3', '1.2.3')
        ([1, 2, 3], [1, 2, 3])
        >>> standardiseVersions(1, 2)
        (1, 2)
        >>> standardiseVersions(1, 1.2)
        (1, 1)
        >>> standardiseVersions(1.2, 1)
        (1, 1)
        >>> standardiseVersions(1.2, '1.2.3')
        ([1, 2], [1, 2])
        >>> standardiseVersions(1, '1.2.3')
        (1, 1)
        >>> standardiseVersions(1.2, '1')
        (1, 1)
        >>> standardiseVersions(1.2, 'v2')
        (1, 2)
        >>> standardiseVersions(1.2, 'v')
        (1, 'v')
        >>> standardiseVersions(1.2, '1.2v3')
        ([1, 2], [1, 2])
        >>> standardiseVersions(1.2, '1v2')
        ([1, 2], [1, 2])
        >>> standardiseVersions('1.2.3', '1.2.3v4')
        ([1, 2, 3], [1, 2, 3])
        >>> standardiseVersions('1.2.3', '1.2.34')
        ([1, 2, 3], [1, 2, 34])
        >>> standardiseVersions('1.2.3', 'v1.2.3')
        ([1, 2, 3], [1, 2, 3])
        >>> standardiseVersions('v1.2.3', 'v1.2')
        ([1, 2], [1, 2])
        >>> standardiseVersions('v1.2.3', 1)
        (1, 1)
        >>> standardiseVersions('1v3', 1.3)
        ([1, 3], [1, 3])
        >>> standardiseVersions(1, '1v3')
        (1, 1)
        >>> standardiseVersions('1.2v3a', '1.2v3b')
        ([1, 2, 3, 'a'], [1, 2, 3, 'b'])
        >>> standardiseVersions('1.2v3a', '1.2v3')
        ([1, 2, 3], [1, 2, 3])
        >>> standardiseVersions('a.1', 'a.2')
        (['a', 1], ['a', 2])
        >>> standardiseVersions('a.b', 'a.d')
        (['a', 'b'], ['a', 'd'])
    """
    aInt = isinstance(a, int)
    aFloat = isinstance(a, float)
    bInt = isinstance(b, int)
    bFloat = isinstance(b, float)

    # Types match
    if aInt and bInt or aFloat and bFloat:
        return a, b
    if aFloat and bInt or bFloat and aInt:
        return int(a), int(b)

    # Split any text into tokens
    # This will result in [prefix, num, separator, ..., suffix], so length 5 for a float
    aTokens = [] if (aInt or aFloat) else tokeniseVersion(str(a))
    aTokenInts = [token for token in aTokens if isinstance(token, int)]
    bTokens = [] if (bInt or bFloat) else tokeniseVersion(str(b))
    bTokenInts = [token for token in bTokens if isinstance(token, int)]

    # If inputs are both strings, then return tokens of the same length
    if aTokens and bTokens:
        tokenLen = min(len(aTokens), len(bTokens))
        return aTokens[:tokenLen], bTokens[:tokenLen]

    # Attempt to map both to float/int
    if aFloat:
        if not bTokenInts:
            return int(a), bTokens[0]
        if len(bTokenInts) >= 2:
            return list(map(int, str(a).split('.'))), bTokenInts[:2]
        return int(a), bTokenInts[0]
    if aInt:
        if bTokenInts:
            return a, bTokenInts[0]
        if bTokens:
            return a, bTokens[0]
    if bFloat:
        if not aTokenInts:
            return aTokens[0], int(b)
        if len(aTokenInts) >= 2:
            return aTokenInts[:2], list(map(int, str(b).split('.')))
        return aTokenInts[0], int(b)
    if bInt:
        if aTokenInts:
            return aTokenInts[0], b
        if aTokens:
            return aTokens[0], b

    # Mapping failed so just return the inputs
    return a, b


def tokeniseVersion(version, ignoreV=True):
    """Take a version string and split it into tokens.

    Parameters:
        version (str): Application version number.
        ignoreV (bool): Ignore `v` if it is the first letter.
            This means `v1.2` will be tokenised as `[1, 2]` rather than
            `['v', 1, 2]`.

    Returns:
        Flat list of integers and strings.

    Tests:
        >>> tokeniseVersion('1')
        [1]
        >>> tokeniseVersion('1.2')
        [1, 2]
        >>> tokeniseVersion('1v2')
        [1, 2]
        >>> tokeniseVersion('1.2.3')
        [1, 2, 3]
        >>> tokeniseVersion('1.2.3v4')
        [1, 2, 3, 4]
        >>> tokeniseVersion('1.2.03v04')
        [1, 2, 3, 4]
        >>> tokeniseVersion('1.2.30v40')
        [1, 2, 30, 40]
        >>> tokeniseVersion('1.2.3v4a')
        [1, 2, 3, 4, 'a']
        >>> tokeniseVersion('a')
        ['a']
        >>> tokeniseVersion('a1')
        ['a', 1]
        >>> tokeniseVersion('a1a')
        ['a', 1, 'a']
        >>> tokeniseVersion('a.b')
        ['a', 'b']
        >>> tokeniseVersion('v1')
        [1]
        >>> tokeniseVersion('12.ab.c34d.5ef6')
        [12, 'ab', 'c34d', 5, 6]
        """
    result = []
    for i, token in enumerate(re.split(r'(\.+)', str(version))[::2]):
        if token.isdigit():
            result.append(int(token))
            continue

        subtokens = re.split(r'(\d+)', token)

        # If any token but the first starts with letter then treat as a word
        if i and subtokens[0]:
            result.append(token)
            continue

        numTokens = len(subtokens)

        # Single letter
        if numTokens == 1:
            result.append(token)
            continue

        # If the first token starts with a letter that isn't "v"
        if not i and subtokens[0] and (not ignoreV or subtokens[0].lower() != 'v'):
            result.append(subtokens[0])

        # Get all integers
        result.extend(int(t) for t in subtokens[1::2])

        # Add on final letter if applicable
        if subtokens[-1]:
            result.append(subtokens[-1])
    return result


if __name__ == '__main__':
    import doctest
    doctest.testmod()
