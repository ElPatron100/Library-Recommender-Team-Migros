# 📚 University Library Recommender System - Team Migros

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_svg)](YOUR_STREAMLIT_LINK_HERE)
[![YouTube Video](https://img.shields.io/badge/YouTube-Video-red?logo=youtube)](YOUR_YOUTUBE_LINK_HERE)

## 📖 Overview
This project aims to enhance the student experience on the university library platform by integrating a personalized recommendation system. By analyzing rental histories, the "You might also like..." feature predicts and suggests academic and leisure materials tailored to individual interests, thereby fostering deeper user engagement and discovery.

To further elevate the overall user experience, the platform introduces three innovative features:
* **Best-seller recommender**: under the personalized recommendation, the reader have access to the list of the 10 books the most read that they have not rented yet.
* **Book Friend Recommender**: This social tool matches readers based on shared reading habits to encourage intellectual exchange and community building. Its ultimate goal is to facilitate book discussions and inspire the formation of local book clubs.
* **Cumulus Fidelity Integration**: Developed in partnership with the Migros group, the app allows readers to earn Cumulus points for every library rental. This incentive program is designed to reward frequent readers and increase long-term fidelity to the library system.


## 🗄 Exploratory Data Analysis (EDA)
Our analysis focused on two primary datasets:
# **Interactions:**
This dataset shows the interaction between the users and the books for the last 2 years. In total the dataset shows 87,047 rental records across 7,838 unique users and 15.109 books.

In average, user rented a total of 11.11 book and each book has been rented an average of 5.76 times. 

![Distribution of the rentals](rentals_per_user_item.png)
This graph shows the distribution of the rentals per users and per items.
The distribution of rentals per user is heavily skewed to the left:
*  **The Majority**: Most users are "casual" readers who have interacted with only 2 to 5 books.
*  **The Tail**: Only less than 13% of users have rented more than 20 items, creating a long tail that stretches toward the right.

The "Rentals per Item" graph shows how the library collection is utilized:
*  **Niche vs. Popular**: The peak indicates that most books have been rented roughly 4 to 6 times.
*  **Concentration**: There is a sharp drop-off after 10 rentals, indicating that only a small fraction of the books (7%) are "bestsellers" with high circulation numbers.



# **Metadata:**
The second important dataset at the origin of our recommender are the metadat about the books. This dataset gives information on 15,109 books, including Titles, Authors, Publisher and Subjects.
Here is an example of the data for 3 different books chosen randomly in the dataset.

#### Example of the item dataset
| ItemID | Title | Author | Publisher | Subjects |
| :--- | :--- | :--- |:--- |:--- |
| 4357 | Charlotte Olivier : la lutte contre la tuberculose dans le canton de Vaud  | Heller, Geneviève | Ed d'en bas | Tuberculosis, Pulmonary--prevention & control; Tuberculosis, Pulmonary--history; lutte contre la tuberculose--Olivier, Charlotte--Vaud (Suisse)--19e s. (fin) / 20e s. (début); Switzerland |
| 9235 | Commentaire du Code pénal suisse / (Art. 1-110) | Logoz, Paul | Delachaux et Niestlé | droit pénal--Suisse--[manuel] |
| 3818 | Petar & Liza | Sekulić-Struja, Miroslav | Actes Sud | Bandes dessinées |

## 🛠 Methodology & Algorithms
Our approach evolved from basic collaborative filtering to a complex hybrid system that integrates user behavior with book metadata.

### 1. Collaborative Filtering (CF)
We began by implementing two foundational collaborative filtering techniques using **Cosine Similarity** to measure the relationship between vectors in our interaction matrix.

* **User-User CF:** This method identifies "neighbor" users who have similar rental histories. If User A and User B have both rented several of the same books, the system recommends other books rented by User B to User A.
* **Item-Item CF:** This method focuses on the relationships between books rather than users. It calculates similarity based on how often two books are rented by the same people. If a student rents a book on "Sociology," the system identifies other books with high similarity scores to that item.

For those two recommencer, the Jaccard similarity was more effective than the cosine similarity seen in class. The Jaccard similarity measures the proportion of shared items between two sets by calculating the size of their intersection divided by the size of their union. In our context, it effectively identifies "reader twins" or similar books by comparing the overlap of binary interactions, rather than measuring the angle between vectors as cosine similarity does.

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

* **Title**: Using text analytics we could use the similarity in books titles to recommend book with close topic as the one already rented
* **Subject**: Utilizing text analytics (IF-XXX) we could use the proximity of the word used in the subject of each book to recommend book with similar subject as the one already rented.
* **History**: analyzing the data, we noticed that the reader had a high probybility of renting again book that they already read, we used this caracteristic as a improvement for our recommender
* **Data Bias**: in the data proposed for this exercise, a reader has a high probability to rent a book with a itemID following the one of book already read. We used this bias to make our recommender even more precise.

When tested in isolation (without the CF base), these techniques were not effective as they lacked the depth of personalized interaction data. The number presented below are not assessed using a cross validation technique, but only on one test set generated in the data (the need in time and energy to assess the precision of all of them using cross validation was too high for the importance of the table.)

#### Individual Component Performance (Before Hybridization)
| Technique | Precision@10 | Recall@10 |
| :--- | :--- | :--- |
| **Title text analytics only** | Low | Low |
| **Subject text analytics only** | Low | Low |
| **History only** | 5.1% | 24.3% |
| **Data Bias only** | Low | Low |


During our process, we tested various other recommender to try to improve the precision of the recommender, but some were not improving the effectiveness:
* **Fame (Popularity):** Utilizing the number of times a book was rented to identify globally popular books was not effective.
* **Author Loyalty:** Identifying authors the user has previously rented to suggest their other works did not improve the overall effectiveness.
* **Publisher Loyalty** Identifying publisher the user has previously rented to suggest their other works did not improve the overall effectiveness.


---

### 4. The Final "All-In" Hybrid Model
The ultimate version of our recommender system combines the high-performing components of **Hybrid 1** (user-user & item-item) with the list of boosters that had a positive impact on the overall result. This ensures that while collaborative patterns drive the results, personal preferences for specific subjects provide the final "nudge" for accuracy.

#### Final Model Configuration & Results
We implemented **5-Fold Cross-Validation** to ensure these results remain consistent across different subsets of our library users.

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
## Limitation

More than x% of the user rented less than x books --> difficult to understand a trend based on that
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
