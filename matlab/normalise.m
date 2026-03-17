% ═══════════════════════════════════════════════════════════════════════
% FILE: normalise.m
% Min-max normalisation — scales every feature column to [0, 1].
%
% Why: without this, features on different scales would bias cosine
% similarity. All 5 features are already 0–1 from Spotify, but we
% normalise anyway as a safety net and to show the LA concept.
%
% Formula per column:  x_scaled = (x - min(x)) / (max(x) - min(x))
% ═══════════════════════════════════════════════════════════════════════
function S_norm = normalise(S)
 
    col_min = min(S);                          % 1x5 — min of each column
    col_max = max(S);                          % 1x5 — max of each column
 
    % ./ = element-wise division (NOT matrix division)
    % Broadcasting: MATLAB applies col_min/col_max across all rows
    S_norm = (S - col_min) ./ (col_max - col_min);
 
    fprintf('Features normalised to [0,1].\n');
end