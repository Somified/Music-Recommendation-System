% FILE: hybrid_similarity.m
% Computes hybrid similarity between a query song and all songs in the dataset.
%
% Formula:
%   hybrid(i) = 0.6 * cosine_similarity(i) + 0.4 * (1 / (1 + euclidean_distance(i)))
%
% The hybrid score captures BOTH:
%   - Direction alignment (cosine)  → are the songs pointing the same way?
%   - Magnitude closeness (euclidean) → how far apart are they in feature space?
%
% LA concepts demonstrated:
%   - Dot product (numerator of cosine)
%   - Vector norms (denominator of cosine + euclidean)
%   - Element-wise subtraction (euclidean distance)
%   - Linear combination of two similarity metrics
%
% Inputs:
%   S_norm     : (n_songs x n_feats) normalised feature matrix
%   query_idx  : integer index of the query song
%   w_cos      : weight for cosine similarity    (default 0.6)
%   w_euc      : weight for euclidean similarity (default 0.4)
%
% Outputs:
%   hybrid_scores : (n_songs x 1) hybrid similarity score for every song
%   cos_scores    : (n_songs x 1) raw cosine similarity scores
%   euc_scores    : (n_songs x 1) raw euclidean similarity scores (1/(1+d))
%   sorted_idx    : indices sorted by hybrid_score descending (query excluded)
%   dot_products  : (n_songs x 1) raw dot products  — for LA transparency
%   norms_songs   : (n_songs x 1) L2 norms of each song vector
% =========================================================================

function [hybrid_scores, cos_scores, euc_scores, sorted_idx, dot_products, norms_songs] = ...
         hybrid_similarity(S_norm, query_idx, w_cos, w_euc)

    % ── Default weights ───────────────────────────────────────────────────
    if nargin < 3, w_cos = 0.6; end
    if nargin < 4, w_euc = 0.4; end

    assert(abs(w_cos + w_euc - 1.0) < 1e-9, ...
           'Weights must sum to 1. Got w_cos=%.2f, w_euc=%.2f', w_cos, w_euc);

    n_songs  = size(S_norm, 1);
    query    = S_norm(query_idx, :)';          % column vector (n_feats x 1)
    query_norm = norm(query, 2);               % scalar L2 norm of query

    if query_norm < 1e-12
        warning('Query vector has near-zero norm. Results may be unreliable.');
        query_norm = 1;
    end

    % ── Pre-compute norms for all songs ──────────────────────────────────
    % norms_songs(i) = ||S_norm(i,:)||_2
    norms_songs = vecnorm(S_norm, 2, 2);       % (n_songs x 1)
    norms_songs(norms_songs < 1e-12) = 1;      % avoid divide-by-zero

    % ── Dot products: (n_songs x n_feats) @ (n_feats x 1) ────────────────
    % dot_products(i) = S_norm(i,:) · query
    dot_products = S_norm * query;             % (n_songs x 1)

    % ── Cosine similarity ─────────────────────────────────────────────────
    % cos(i) = (S_norm(i,:) · query) / (||S_norm(i,:)|| * ||query||)
    cos_scores = dot_products ./ (norms_songs * query_norm);   % (n_songs x 1)
    cos_scores = max(0, cos_scores);           % clamp negatives to 0

    % ── Euclidean distance → similarity ──────────────────────────────────
    % diff(i,:) = S_norm(i,:) - query'
    % euc_dist(i) = ||S_norm(i,:) - query'||_2
    % euc_sim(i)  = 1 / (1 + euc_dist(i))   ∈ (0, 1]
    diff_mat    = S_norm - query';             % broadcast: (n_songs x n_feats)
    euc_dist    = vecnorm(diff_mat, 2, 2);     % (n_songs x 1)
    euc_scores  = 1 ./ (1 + euc_dist);        % (n_songs x 1)

    % ── Hybrid linear combination ─────────────────────────────────────────
    % hybrid(i) = w_cos * cos(i) + w_euc * euc_sim(i)
    hybrid_scores = w_cos * cos_scores + w_euc * euc_scores;   % (n_songs x 1)

    % ── Normalise to [0, 1] ───────────────────────────────────────────────
    % Zero out the query song first (it would always be rank 1 otherwise)
    hybrid_scores(query_idx) = 0;
    cos_scores(query_idx)    = 0;
    euc_scores(query_idx)    = 0;

    mx = max(hybrid_scores);
    if mx > 0
        hybrid_scores = hybrid_scores / mx;
    end

    % ── Sort descending by hybrid score (query already zeroed) ───────────
    [~, sorted_idx] = sort(hybrid_scores, 'descend');
    sorted_idx = sorted_idx(sorted_idx ~= query_idx);   % belt-and-braces remove query

    % ── Print summary ─────────────────────────────────────────────────────
    fprintf('\n── Hybrid Similarity Summary ──────────────────────────\n');
    fprintf('  w_cos=%.2f  w_euc=%.2f\n', w_cos, w_euc);
    fprintf('  query norm  : %.4f\n', query_norm);
    fprintf('  max dot prod: %.4f   min dot prod: %.4f\n', max(dot_products), min(dot_products));
    fprintf('  max cos     : %.4f   max euc_sim : %.4f\n', max(cos_scores), max(euc_scores));
    fprintf('  score range : [%.4f, %.4f]\n', min(hybrid_scores), max(hybrid_scores));
    fprintf('────────────────────────────────────────────────────────\n\n');

end