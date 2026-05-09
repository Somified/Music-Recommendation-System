# Melodix — Explainable Linear Algebra Based Music Recommendation System

## Overview

Melodix is an explainable music recommendation system built using core Linear Algebra concepts. The project represents songs as vectors in an 8-dimensional feature space and generates recommendations based on similarity to a user’s musical taste profile.

Unlike black-box recommendation systems, Melodix focuses on transparency and interpretability by exposing the mathematical computations behind every recommendation.

The user selects a few seed songs, and the system computes a “taste centroid” representing the average musical preference. Songs closest to this centroid are recommended using multiple similarity measures.

---

# Objective

The objective of this project is to demonstrate the practical application of Linear Algebra in recommender systems through:

* Vector representation of songs
* Matrix-based data storage
* Centroid computation
* Cosine similarity
* Euclidean distance
* Feature normalization
* Explainable recommendation logic

---

# Technologies Used

* Python
* MATLAB
* Streamlit
* Spotify Audio Features Dataset

---

# Core Linear Algebra Concepts Used

## 1. Vectors

Each song is represented as an 8-dimensional vector:

[
S =
[\text{energy}, \text{danceability}, \text{valence}, \text{acousticness}, \text{speechiness}, \text{instrumentalness}, \text{liveness}, \text{tempo}]
]

Each dimension corresponds to one musical feature.

---

# 2. Vector Space

All songs exist in a shared 8-dimensional vector space.

Each song becomes a point in this geometric space, allowing similarity computations between songs.

---

# 3. Matrix Representation

The complete dataset is stored as a matrix:

[
A_{m \times 8}
]

where:

* (m) = number of songs
* 8 = number of features

Each row represents one song vector.

---

# 4. Z-Score Standardization

Before similarity calculations, features are standardized using z-score normalization:

[
z=\frac{x-\mu}{\sigma}
]

This ensures that features with larger scales do not dominate the recommendation process.

---

# 5. Taste Centroid Computation

The user selects multiple seed songs:

[
S_1, S_2, S_3, ..., S_n
]

The system computes the centroid:

[
C=\frac{S_1+S_2+S_3+\dots+S_n}{n}
]

This centroid acts as the mathematical representation of the user’s average music taste.

---

# 6. Dot Product

The dot product is used inside cosine similarity calculations:

[
s \cdot c =
s_1c_1+s_2c_2+\dots+s_nc_n
]

It measures alignment between vectors.

---

# 7. Vector Norm / Magnitude

Vector magnitude is computed as:

[
||s||=
\sqrt{s_1^2+s_2^2+\dots+s_n^2}
]

This represents the length of a vector.

---

# 8. Cosine Similarity

Cosine similarity measures directional similarity between song vectors and the centroid:

[
\cos(\theta)=\frac{s\cdot c}{||s|| \ ||c||}
]

Higher cosine values indicate greater similarity.

Cosine similarity measures directional similarity rather than magnitude.

In simple terms:

songs with similar feature patterns point in similar directions in vector space
higher cosine values mean greater similarity

This is one of the most important similarity measures in recommender systems.

### Why Cosine Similarity?

Cosine similarity compares orientation rather than magnitude. In recommendation systems, proportional feature patterns matter more than absolute values.

---

# 9. Euclidean Distance

Euclidean distance measures absolute closeness between vectors:

[
d(s,c)=||s-c||
]

Expanded form:

[
d(s,c)=
\sqrt{
(s_1-c_1)^2+(s_2-c_2)^2+\dots+(s_n-c_n)^2
}
]
This measures the actual distance between the song vector and centroid vector.
Smaller distance indicates stronger similarity.
Unlike cosine similarity, Euclidean distance considers absolute closeness in feature space.

---

# 10. Hybrid Similarity System

The project combines:

* Cosine similarity
* Euclidean distance
* Feature-wise matching
* Geometric mean aggregation

This hybrid approach improves robustness and recommendation quality.
Cosine similarity checks whether feature patterns are aligned.
Euclidean distance checks how close the actual values are.

Using both avoids inaccurate recommendations that may have similar direction but large numerical differences.

### Why Combine Cosine and Euclidean?

* Cosine similarity captures directional similarity.
* Euclidean distance captures absolute proximity.

Using both prevents inaccurate recommendations caused by relying on only one metric.

---

# 11. Geometric Mean Aggregation

Feature match scores are combined using geometric mean:

[
\text{Geo Mean} =
\exp(\text{mean}(\log(match)))
]

This rewards songs that perform consistently across all dimensions rather than excelling in only one feature.

---

# 12. Explainability Features

A major focus of the project is recommendation transparency.

The system includes:

* Per-feature similarity heatmaps
* Dot product and norm displays
* Cosine similarity calculations
* Euclidean distance calculations
* Radar charts
* Feature contribution breakdowns
* Recommendation score transparency
* Similarity scaling interpretation

This allows users to understand *why* a song was recommended.

---

# 13. Radar Chart Visualization

The radar chart visualizes:

* seed songs
* centroid vector
* recommended songs

in multi-dimensional feature space.

This helps users intuitively understand the structure of musical similarity.

---

# 14. Recommendation Score Scaling

Initially, raw similarity values occupied a very narrow numerical range.

Example:

* 72.6
* 72.5
* 72.4

Although mathematically correct, such compressed scores reduced interpretability and visual distinction between recommendations.

To improve readability while preserving ranking order, min-max scaling was applied:

[
\text{Scaled Score} =
\frac{x-x_{min}}{x_{max}-x_{min}}
]

The scores were then stretched into a more interpretable range.

This improved:

* visual differentiation
* recommendation clarity
* interpretability of rankings

without changing the underlying recommendation order.

---

# 15. Weighted Hybrid Recommendation Logic

The final recommendation score combines multiple similarity metrics using weighted aggregation:

* Cosine Similarity → 50%
* Euclidean Similarity → 30%
* Feature Consistency / Geometric Mean → 20%

This ensures that:

* directional similarity is considered
* geometric proximity is considered
* feature consistency is rewarded

The weighted hybrid system produces more balanced and realistic recommendations.

---

# 16. MATLAB Visualization and Statistical Analysis

MATLAB was used to create additional analytical visualizations supporting the recommendation system.

These visualizations strengthen the mathematical interpretation of the project.

---

# 17. 3D Feature Space Visualization

A 3D vector-space visualization was created using:

* Energy (X-axis)
* Danceability (Y-axis)
* Valence (Z-axis)

The graph visualizes:

* all songs in the dataset
* selected seed songs
* the taste centroid
* recommended songs

The centroid acts as the geometric center of user preference.

Recommended songs are selected based on proximity and similarity to this centroid.

This visualization demonstrates:

* vectors in feature space
* geometric clustering
* centroid-based recommendation logic
* vector-space similarity analysis

---

# 18. Before vs After Normalization Analysis

A normalization comparison graph was generated to demonstrate the importance of z-score standardization.

Before normalization:

* features existed on vastly different scales
* tempo dominated similarity computations

After normalization:

* all features shared comparable scales
* each feature contributed fairly to calculations

The graph validates:

* matrix column-wise mean normalization
* standard deviation standardization
* balanced vector-space representation

---

# 19. Statistical Validation of Standardization

The project validates normalization mathematically by showing:

* post-normalization mean:

[
\mu \approx 0
]

* post-normalization standard deviation:

[
\sigma \approx 1
]

This confirms successful standardization of feature dimensions.

---

# 20. Heatmap-Based Explainability

The heatmap visualization displays feature-wise matching between:

* seed songs
* centroid vector
* recommended songs

This provides transparency by showing which features contributed most strongly to similarity.

Instead of acting as a black-box recommender, the system visually explains recommendation reasoning.

---

# Project Workflow

## Step 1 — User Selects Seed Songs

The user selects 3–5 songs based on personal preference.

---

## Step 2 — Feature Extraction

Spotify audio features are extracted for each selected song.

---

## Step 3 — Standardization

All features are standardized using z-score normalization.

---

## Step 4 — Centroid Computation

The system computes the average preference vector (taste centroid).

---

## Step 5 — Similarity Computation

Every song in the dataset is compared against the centroid using:

* cosine similarity
* Euclidean distance
* feature matching

---

## Step 6 — Hybrid Score Aggregation

Multiple similarity measures are combined into a final weighted recommendation score.

---

## Step 7 — Recommendation Ranking

Songs with the highest overall similarity are ranked and recommended.

---

# Academic Significance

This project demonstrates how Linear Algebra can be applied to:

* recommender systems
* similarity analysis
* vector-space modeling
* geometric interpretation of data
* statistical normalization
* explainable AI systems

The project also emphasizes explainable recommendation systems rather than opaque black-box approaches.

---

# Key Strengths

* Strong application of Linear Algebra concepts
* Real-world recommendation system implementation
* Explainable and transparent computations
* Interactive visualization tools
* Hybrid similarity methodology
* Practical use of vector-space modeling
* MATLAB-based analytical validation
* Statistical normalization verification
* Interactive recommendation transparency

---

# Project Features

* Interactive Streamlit interface
* Seed-song based recommendations
* Heatmap-based feature matching
* Dot product and norm transparency
* Radar chart visualization
* MATLAB analytical graphs
* Weighted recommendation scoring
* Recommendation score scaling
* Centroid-based recommendation engine
* Feature contribution analysis

---

# Viva Questions and Answers

## Why use cosine similarity?

Cosine similarity measures directional similarity between vectors, making it useful for comparing feature patterns.

---

## Why use z-score normalization?

Normalization prevents large-scale features from dominating similarity calculations.

---

## Why use a centroid?

The centroid represents the user’s average musical preference across multiple songs.

---

## Why combine cosine and Euclidean distance?

Cosine captures orientation similarity while Euclidean captures numerical closeness.

---

## Why use geometric mean?

Geometric mean penalizes imbalance and rewards songs that consistently match across all features.

---

## Why use weighted aggregation?

Different similarity measures capture different aspects of recommendation quality. Weighted aggregation balances these factors.

---

## Why were scores scaled?

Raw similarity values occupied a narrow range, so scaling improved interpretability and visual distinction while preserving ranking order.

---

## What does the 3D graph represent?

The graph visualizes songs as vectors in feature space and demonstrates centroid-based recommendation logic.

---

# Final Project Framing

Melodix can be described as:

> “An explainable music recommendation engine using centroid-based similarity analysis in standardized vector space.”

This project demonstrates the intersection of:

* Linear Algebra
* Geometry
* Data Representation
* Similarity Analysis
* Statistical Standardization
* Explainable Recommendation Systems
* Interactive Visualization
* Vector-Space Modeling
