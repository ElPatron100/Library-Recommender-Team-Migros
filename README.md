# 📚 University Library Recommender System - Team Migros

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_svg)](YOUR_STREAMLIT_LINK_HERE)
[![YouTube Video](https://img.shields.io/badge/YouTube-Video-red?logo=youtube)](YOUR_YOUTUBE_LINK_HERE)

## 📖 Overview
This project aims to improve the student experience on the university library platform. By building a recommendation system, we predict books that students are likely to enjoy based on their rental history. This "You might also like..." functionality is designed to increase engagement and help users discover relevant academic and leisure materials.

## 🗄 Exploratory Data Analysis (EDA)
Our analysis focused on two primary datasets:
# **Interactions:**
This dataset shows the interaction between the users and the books for the last X years. In total the dataset shows 87,047 rental records across 7,838 unique users and 15.109 books.
In average, user rented a total of X book and each book has been rented a total of x times. 
It is important to highlight that a small number of books (the "bestsellers") account for a large portion of the interactions, while many books have only been rented once or twice. Indeed, X% of the book represent more than X% of the rentals. The same element can be analysed for the user since x% of the user did x% of the rental.
![Description of the heatmap](heatmap.png)
This heatmap shows the interactions between the first user and the first books.

# **Metadata:**
The second important dataset at the origin of our recommender are the metadat about the books. This dataset gives information on 15,109 books, including Titles, Authors, and Subjects. add something about the distribution between authors, subjects, ...


## 🛠 Methodology & Algorithms
Our approach evolved from basic collaborative filtering to a complex hybrid system that integrates user behavior with book metadata.

### 1. Collaborative Filtering (CF)
We began by implementing two foundational collaborative filtering techniques using **Cosine Similarity** to measure the relationship between vectors in our interaction matrix.

* **User-User CF:** This method identifies "neighbor" users who have similar rental histories. If User A and User B have both rented several of the same books, the system recommends other books rented by User B to User A.
* **Item-Item CF:** This method focuses on the relationships between books rather than users. It calculates similarity based on how often two books are rented by the same people. If a student rents a book on "Sociology," the system identifies other books with high similarity scores to that item.

### 2. The First Hybrid & Weight Optimization
We realized that neither model was perfect on its own. To find the "sweet spot," we created **Hybrid 1**, which combines the prediction scores of both models. We ran an optimization loop testing different weight ratios (from 5/95 to 95/5) to maximize **Precision@10**.

**Optimal Weight Found:** **58% User-User / 42% Item-Item**.

#### Initial Performance Comparison
| Model | Precision@10 | Recall@10 |
| :--- | :--- | :--- |
| **User-User CF** | 0.1705 | 0.8862 |
| **Item-Item CF** | 0.1608 | 0.8076 |
| **Hybrid 1 (58/42)** | **0.1809** | **0.XXXX** |

---

### 3. Integrating Additional Elements
To further refine the recommendations, we experimented with three metadata-driven "boosters":

* **Fame (Popularity):** Utilizing **Logarithmic Scaling** to identify globally popular books while dampening the "superstar" effect.
* **Author Loyalty:** Identifying authors the user has previously rented to suggest their other works.
* **Subject Matching:** Boosting books that share the same classification or subjects as the user's history.

When tested in isolation (without the CF base), these techniques were not effective as they lacked the depth of personalized interaction data.

#### Individual Component Performance (Before Hybridization)
| Technique | Precision@10 | Recall@10 |
| :--- | :--- | :--- |
| **Fame Only** | Low | Low |
| **Author Boost Only** | Low | Low |
| **Subject Boost Only** | Low | Low |

---

### 4. The Final "All-In" Hybrid Model
The ultimate version of our recommender system combines the high-performing **Hybrid 1** with these boosters. This ensures that while collaborative patterns drive the results, personal preferences for specific authors and subjects provide the final "nudge" for accuracy.

#### Final Model Configuration & Results
We implemented **5-Fold Cross-Validation** to ensure these results remain consistent across different subsets of our library users[cite: 455, 477].

| Component | Weight (%) | 
| :--- | :--- |
| **User-User CF** | 49% |
| **Item-Item CF** | 39% |
| **Author Boost** | 10% |
| **Fame (Pop)** | 2% | 
| **Total** | **100%** | 


| Final Model | Final Precision@10 | Final Recall@10 |
| :--- | :--- | :--- |
| **Hybrid 2** | 0.XXX| 0.XXX|
---

### 5. Additional Note
To maintain scientific integrity while ensuring the highest possible recommendation quality, we adopted a dual-phase training and evaluation strategy:
*  **Validation Phase**: For all performance metrics (Precision@10 and Recall@10) reported in our methodology tables, we utilized a temporal 80/20 train-test split combined with 5-fold cross-validation. This allowed us to rigorously assess the predictive power of each model on "unseen" data without any data leakage.

*  **Production Phase**: Once the optimal hyperparameters and weights were identified via validation, we retrained the final model using 100% of the available interaction data. This "all-in" approach was used to generate our final Kaggle submissions and powers our Streamlit user interface, ensuring the system leverages every available data point to provide the most accurate real-world recommendations.
---

## 📊 Performance Demonstration

Let's see a demonstration of how our user interface is working.

### Good example - user XX

User XX:
*  Past rentals: ...
*  Our recommendation: ...

We can see that based on the past item rented our model understood that this reader liked XX books. Using that and the fame of the book ...

### Good example - user XX

User XX:
*  Past rentals: ...
*  Our recommendation: ...

We can see that the model recommend XX to the user X even if it seems not relevant at all. A potential explanation could be that...



---

## 💻 User Interface (Streamlit)

Explanation of our User interface written by EL PATRON

---

## 📺 Project Video
Our YouTube video includes a presentation of the interface, ...

[**Watch the Presentation & Demo Here**](YOUR_YOUTUBE_LINK_HERE)

---

## 👩‍💻 Logistics
* **Team Name:** Migros - Micha Streuli & Noé Délèze
* **Kaggle Leaderboard Score:** 0.XXXX (Top X%)

---
