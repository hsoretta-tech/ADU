def normalize_code_tokens(s: str) -> str:
    if s is None:
        return ""
    s = s.replace('"', "'")
    try:
        out_tokens = []
        sio = io.StringIO(s)
        for tok in tokenize.generate_tokens(sio.readline):
            toknum = tok.type
            tokval = tok.string
            if toknum == tokenize.COMMENT:
                continue
            out_tokens.append(tokval)
        s = "".join(out_tokens)
    except Exception:
        s = re.sub(r"#.*", "", s)

    # IMPORTANT FIX: preserve indentation and structure
    s = "\n".join(line.strip() for line in s.splitlines() if line.strip())

    s = s.strip().rstrip(";")
    return s


def is_correct_submission(submitted: str, expected: str) -> bool:
    try:
        sub_ast = ast.parse(submitted)
        exp_ast = ast.parse(expected)
        return ast.dump(sub_ast, include_attributes=False) == ast.dump(exp_ast, include_attributes=False)
    except Exception:
        return normalize_code_tokens(submitted) == normalize_code_tokens(expected)
