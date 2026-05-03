% FILE: pillar3_ratings.m
% Pillar 3 — Rating Matrix
% Predicts a score for each song using row/col means of R.
% =========================================================================

function p3_scores = pillar3_ratings(R)

    if isempty(R)
        warning('R matrix is empty. Pillar 3 scores set to zero.');
        p3_scores = [];
        return;
    end

    [n_users, n_songs] = size(R);

    % ── Row means (user preference level)
    user_means = mean(R, 2);          % n_users × 1

    % ── Column means (song popularity)
    song_means = mean(R, 1);          % 1 × n_songs

    % ── Global mean
    global_mean = mean(R(:));

    % ── Predicted rating matrix
    R_predicted = user_means + song_means - global_mean;

    % Clamp values to [0,1]
    R_predicted = max(0, min(1, R_predicted));

    % ── Final score per song
    p3_scores = mean(R_predicted, 1)';   % column vector

    % Normalize to [0,1]
    mn = min(p3_scores);
    mx = max(p3_scores);

    if mx > mn
        p3_scores = (p3_scores - mn) / (mx - mn);
    else
        p3_scores = zeros(n_songs, 1);
    end

    fprintf('Pillar 3 done. Score range: [%.3f, %.3f]\n', ...
            min(p3_scores), max(p3_scores));

end