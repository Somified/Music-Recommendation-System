% FILE: pillar1_similarity.m
% Finds songs most similar to a query song using cosine similarity.
%
% MATH:
%   sim(a, b) = (a · b) / (‖a‖ × ‖b‖)
%
%   - dot(a,b)  = dot product  = sum of element-wise products
%   - norm(a)   = magnitude    = sqrt(sum of squares)
%   - Dividing by both norms scales result to [-1, 1]
%   - sim = 1.0 → identical direction (same vibe)
%   - sim = 0.0 → perpendicular (nothing in common)
% ═══════════════════════════════════════════════════════════════════════
function [scores, sorted_idx] = pillar1_similarity(S, query_idx)
 
    query     = S(query_idx, :);      % 1×5 row vector — the query song
    num_songs = size(S, 1);
    scores    = zeros(num_songs, 1);  % pre-allocate result vector
 
    for i = 1:num_songs
        candidate = S(i, :);
 
        % COSINE SIMILARITY — the core LA formula
        scores(i) = dot(query, candidate) / ...
                    (norm(query) * norm(candidate));
    end
 
    % Sort highest to lowest similarity
    [scores, sorted_idx] = sort(scores, 'descend');
end