% FILE: pillar2_taste.m
% Builds a user taste vector from liked songs and finds best matches.
%
% MATH:
%   taste = (s₁ + s₂ + ... + sₙ) / n   ← centroid of liked songs
%
%   This is a LINEAR COMBINATION — the arithmetic mean of vectors.
%   taste is a new vector in ℝ⁵ representing the user's "average" song.
%   We then find songs with highest cosine similarity to this vector.
% ═══════════════════════════════════════════════════════════════════════
function [taste_vec, scores, sorted_idx] = pillar2_taste(S, liked_indices)
 
    liked_songs = S(liked_indices, :);    % k×5 submatrix of liked songs
 
    % mean(M, 1) = column-wise mean = centroid vector
    taste_vec = mean(liked_songs, 1);     % 1×5 taste vector
 
    fprintf('Taste vector: energy=%.2f  dance=%.2f  valence=%.2f  acoustic=%.2f  tempo=%.2f\n', ...
            taste_vec(1), taste_vec(2), taste_vec(3), taste_vec(4), taste_vec(5));
 
    num_songs = size(S, 1);
    scores    = zeros(num_songs, 1);
 
    for i = 1:num_songs
        candidate = S(i, :);
        scores(i) = dot(taste_vec, candidate) / ...
                    (norm(taste_vec) * norm(candidate));
    end
 
    [scores, sorted_idx] = sort(scores, 'descend');
end