"""Contextual joins for connected runs, without word-specific ligatures."""


def chain_feature_code(pairs, contextual_pairs=()):
    classes = []
    mark = []
    extend = []
    resolve = []
    members = sorted(set("".join(pairs)))
    for suffix, tag in [("", ""), (".sc", "_sc")]:
        for middle in members:
            lefts = sorted({pair[0] for pair in pairs if pair[1] == middle})
            rights = sorted({pair[1] for pair in pairs if pair[0] == middle})
            if not lefts or not rights:
                continue
            left_class = f"@ChainLeft_{middle}{tag}"
            right_class = f"@ChainRight_{middle}{tag}"
            classes.append(
                f"{left_class} = ["
                + " ".join(f"{c}{suffix} {c}.chain{suffix}" for c in lefts)
                + "];"
            )
            classes.append(
                f"{right_class} = ["
                + " ".join(f"{c}{suffix} {c}.chain{suffix}" for c in rights)
                + "];"
            )
            mark.append(
                f"sub {left_class} {middle}{suffix}' {right_class} by {middle}.chain{suffix};"
            )
        # These connections have no compound glyph, including in isolated pairs.
        for left, right in sorted(contextual_pairs):
            mark.append(f"sub {left}{suffix}' {right}{suffix} by {left}.chain{suffix};")
        for left, right in pairs:
            extend.append(
                f"sub {left}{suffix}' {right}.chain{suffix} by {left}.chain{suffix};"
            )
            extend.append(
                f"sub {left}.chain{suffix} {right}{suffix}' by {right}.chain{suffix};"
            )
            resolve.append(
                f"sub {left}.chain{suffix}' {right}.chain{suffix} by {left}.join_{right}{suffix};"
            )
    rules = []
    for name, statements in [
        ("MarkChains", mark),
        ("ExtendChains", extend),
        ("ResolveChains", resolve),
    ]:
        rules.extend([f"lookup {name} {{", *statements, f"}} {name};"])
    return classes, rules
