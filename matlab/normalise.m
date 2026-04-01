function S_norm = normalise(S)

    col_min   = min(S);
    col_max   = max(S);
    col_range = col_max - col_min;

    col_range(col_range == 0) = 1;

    S_norm = (S - col_min) ./ col_range;

    fprintf('Features normalised to [0,1].\n');
end