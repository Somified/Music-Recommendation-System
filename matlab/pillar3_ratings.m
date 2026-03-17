% FILE: pillar3_ratings.m
% Predicts song ratings using the ratings matrix R.
%
% MATH:
%   R is (users × songs). 0 = unrated.
%
%   predicted(j) = (user_mean + song_mean(j)) / 2
%
%   user_mean    = avg of all ratings this user gave
%   song_mean(j) = avg rating song j received across all users
%
%   This is a simple ROW/COLUMN OPERATION on a matrix.
%   No SVD needed — pure Sem 2 linear algebra.
% ═══════════════════════════════════════════════════════════════════════
function [predicted, sorted_idx] = pillar3_ratings(R, user_idx)
 
    [~, num_songs] = size(R);
 
    % User mean — average of all non-zero ratings this user gave
    user_row  = R(user_idx, :);
    rated     = user_row(user_row > 0);
    user_mean = mean(rated);
 
    % Song means — for each song, average across all users who rated it
    song_means = zeros(1, num_songs);
    for j = 1:num_songs
        col          = R(:, j);
        rated_values = col(col > 0);
        if ~isempty(rated_values)
            song_means(j) = mean(rated_values);
        end
    end
 
    % Predicted score = average of user tendency and song quality
    % This is a LINEAR COMBINATION of two signals
    predicted = (user_mean + song_means) / 2;
 
    % Zero out already-rated songs — don't re-recommend them
    predicted(user_row > 0) = 0;
 
    [predicted, sorted_idx] = sort(predicted, 'descend');
end