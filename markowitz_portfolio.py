"""
OPTIMISATION DE PORTEFEUILLE - MODELE DE MARKOWITZ
Auteur : Aymane El Adlouni

Ce programme applique la theorie moderne du portefeuille de Harry Markowitz
a un panier d'actions de la Bourse de Casablanca. L'objectif est de trouver
la meilleure repartition possible du capital entre plusieurs actions.

Idee centrale : le risque d'un portefeuille ne depend pas seulement du risque
de chaque action, mais aussi de la maniere dont les actions bougent ensemble.
En combinant des actifs peu correles, on reduit le risque global sans forcement
sacrifier le rendement. C'est la diversification, mesuree mathematiquement.

Etapes du modele :
    1. Definir les actions et leurs caracteristiques (rendement, risque)
    2. Construire la matrice de correlation entre les actions
    3. Generer des milliers de portefeuilles avec des ponderations aleatoires
    4. Calculer le rendement et le risque de chaque portefeuille
    5. Tracer la frontiere efficiente
    6. Identifier le portefeuille optimal (meilleur ratio de Sharpe)
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


# Actions reelles de la Bourse de Casablanca retenues pour l'analyse.
# Les rendements annuels attendus et les volatilites sont des estimations
# realistes servant a illustrer la methode ; dans un projet reel ils seraient
# calcules a partir de l'historique des cours.
actions = ["Attijariwafa Bank", "Maroc Telecom", "LafargeHolcim Maroc",
           "BCP", "Cosumar", "Marsa Maroc"]

rendements_attendus = np.array([0.11, 0.06, 0.09, 0.10, 0.07, 0.12])
volatilites = np.array([0.20, 0.14, 0.22, 0.19, 0.16, 0.25])

# Taux sans risque : rendement des bons du Tresor marocains (approx.).
# Il sert de reference pour calculer le ratio de Sharpe.
taux_sans_risque = 0.03


def construire_matrice_covariance():
    """
    Construit la matrice de covariance a partir des correlations entre actions.

    La correlation mesure a quel point deux actions bougent ensemble :
    proche de 1 elles evoluent dans le meme sens, proche de 0 elles sont
    independantes, negative elles evoluent en sens inverse. C'est ce qui
    permet la diversification.
    """
    n = len(actions)
    correlations = np.array([
        [1.00, 0.30, 0.45, 0.65, 0.25, 0.35],
        [0.30, 1.00, 0.20, 0.28, 0.22, 0.18],
        [0.45, 0.20, 1.00, 0.40, 0.30, 0.38],
        [0.65, 0.28, 0.40, 1.00, 0.26, 0.33],
        [0.25, 0.22, 0.30, 0.26, 1.00, 0.20],
        [0.35, 0.18, 0.38, 0.33, 0.20, 1.00],
    ])

    # Covariance entre deux actions = correlation x volatilite_1 x volatilite_2
    covariance = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            covariance[i][j] = correlations[i][j] * volatilites[i] * volatilites[j]

    return covariance, correlations


def perf_portefeuille(poids, covariance):
    """
    Calcule le rendement et le risque d'un portefeuille donne.

    Le rendement est la moyenne des rendements ponderee par les poids.
    Le risque tient compte des covariances : c'est la ou la diversification
    joue, car les actions peu correlees reduisent le risque total.
    """
    rendement = np.sum(poids * rendements_attendus)
    variance = np.dot(poids, np.dot(covariance, poids))
    risque = np.sqrt(variance)
    return rendement, risque


def simuler_portefeuilles(covariance, n_portefeuilles=20000):
    """
    Genere des milliers de portefeuilles avec des ponderations aleatoires.

    Pour chacun, on tire des poids au hasard (dont la somme fait 100%),
    puis on calcule son rendement, son risque et son ratio de Sharpe.
    Le nuage de points obtenu dessine l'ensemble des portefeuilles possibles.
    """
    n = len(actions)
    resultats = {
        "rendement": [],
        "risque": [],
        "sharpe": [],
        "poids": [],
    }

    for _ in range(n_portefeuilles):
        poids = np.random.random(n)
        poids = poids / np.sum(poids)

        rendement, risque = perf_portefeuille(poids, covariance)
        sharpe = (rendement - taux_sans_risque) / risque

        resultats["rendement"].append(rendement)
        resultats["risque"].append(risque)
        resultats["sharpe"].append(sharpe)
        resultats["poids"].append(poids)

    return resultats


def afficher_actions(correlations):
    """Affiche les caracteristiques des actions et leur correlation."""
    print("Actions du portefeuille")
    tableau = pd.DataFrame({
        "Action": actions,
        "Rendement attendu": [f"{r*100:.1f}%" for r in rendements_attendus],
        "Volatilite": [f"{v*100:.1f}%" for v in volatilites],
    })
    print(tableau.to_string(index=False))
    print()

    print("Matrice de correlation")
    corr_df = pd.DataFrame(correlations,
                           index=[a[:12] for a in actions],
                           columns=[a[:8] for a in actions])
    print(corr_df.to_string())
    print()


def afficher_optimal(resultats):
    """Identifie et affiche le portefeuille au meilleur ratio de Sharpe."""
    idx = np.argmax(resultats["sharpe"])
    poids_opt = resultats["poids"][idx]

    print("Portefeuille optimal (meilleur ratio de Sharpe)")
    print(f"Rendement attendu : {resultats['rendement'][idx]*100:.1f}%")
    print(f"Risque (volatilite) : {resultats['risque'][idx]*100:.1f}%")
    print(f"Ratio de Sharpe : {resultats['sharpe'][idx]:.3f}")
    print()

    print("Repartition du capital")
    repartition = pd.DataFrame({
        "Action": actions,
        "Allocation": [f"{p*100:.1f}%" for p in poids_opt],
    }).sort_values("Allocation", ascending=False)
    print(repartition.to_string(index=False))
    print()

    return idx


def tracer_frontiere(resultats, idx_optimal):
    """
    Trace le nuage des portefeuilles simules et met en evidence l'optimal.

    Chaque point est un portefeuille, colore selon son ratio de Sharpe.
    Le bord superieur gauche du nuage est la frontiere efficiente : les
    meilleurs portefeuilles possibles pour chaque niveau de risque.
    """
    plt.figure(figsize=(11, 7))

    dispersion = plt.scatter(
        resultats["risque"], resultats["rendement"],
        c=resultats["sharpe"], cmap="viridis", s=8, alpha=0.5
    )
    plt.colorbar(dispersion, label="Ratio de Sharpe")

    # Portefeuille optimal marque d'une etoile rouge
    plt.scatter(
        resultats["risque"][idx_optimal],
        resultats["rendement"][idx_optimal],
        color="red", marker="*", s=500, edgecolors="black",
        label="Portefeuille optimal", zorder=5
    )

    plt.xlabel("Risque (volatilite annuelle)")
    plt.ylabel("Rendement attendu annuel")
    plt.title("Frontiere efficiente - Actions de la Bourse de Casablanca")
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig("markowitz_frontiere.png", dpi=120)
    print("Graphique enregistre : markowitz_frontiere.png")


if __name__ == "__main__":
    np.random.seed(42)

    covariance, correlations = construire_matrice_covariance()
    afficher_actions(correlations)

    resultats = simuler_portefeuilles(covariance)
    idx_optimal = afficher_optimal(resultats)
    tracer_frontiere(resultats, idx_optimal)
