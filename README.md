# 🎮 Pokémon JVSI — Édition Aventure

> Jeu de rôle Pokémon fait maison en Python / Pygame — exploration, combats au tour par tour, champions d'arène, évolutions et Pokédex complet.

---

## 📸 Aperçu

| Menu principal | Exploration | Combat |
|:-:|:-:|:-:|
| Background custom, musique, plein écran | Carte à zones, HUD équipe | Animations, types, captures |

---

## ✨ Fonctionnalités

- **Exploration libre** sur une carte 15×10 à 7 zones distinctes (Plaine, Forêt, Montagne, Océan, Grotte, Ciel, Ville)
- **Combats au tour par tour** avec calcul de types, coups critiques, attaques spéciales et animations
- **71 Pokémon** entièrement originaux, avec sprites, types et stats dans un Pokédex JSON
- **Système d'évolution** : évolutions classiques par niveau + Forme Ultime (reset niveau 5 / stats ×1.8)
- **Champions d'Arène** : Sylvan (Plante) et Ignis (Feu) — combat 6v6, dialogues, badges et récompenses
- **Pokédex dynamique** : suivi des Pokémon vus et capturés, taux de complétion
- **Sauvegarde/Chargement** en JSON (équipe, réserve, position, inventaire)
- **Créateur de Pokémon** intégré pour ajouter ses propres créatures
- **Menu adaptatif** : background image, musique de fond, plein écran, volume — tout paramétrable

## 🚀 Installation

### Prérequis

- Python **3.13**
- Pygame **2.x**



## 🎮 Contrôles

### Exploration
| Touche | Action |
|--------|--------|
| `Z Q S D` / Flèches | Déplacement |
| `E` | Menu Équipe |
| `R` | Réserve (en ville) |
| `H` | Soigner l'équipe (en ville) |
| `P` | Pokédex |
| `G` | Sauvegarder |
| `ESC` | Retour au menu principal |

### Combat
| Touche | Action |
|--------|--------|
| `A` | Attaque normale |
| `S` | Attaque spéciale (50% critique ×2) |
| `X` | Changer de Pokémon |
| `P` | Utiliser une Potion |
| `C` | Lancer une Pokéball |
| `F` | Fuir |

### Menu Équipe
| Touche | Action |
|--------|--------|
| `↑ ↓` | Naviguer |
| `Entrée` | Mettre en actif |
| `E` | Évoluer (si disponible) |
| `U` | Forme Ultime (niveau ≥ 30) |

---

## 🗺️ Les zones

| Zone | Couleur | Taux rencontre | Pokémon notables |
|------|---------|---------------|-----------------|
| Plaine Verdoyante | Vert clair | 15% | Keunotor, Flamydra |
| Forêt Mystique | Vert foncé | 20% | Verdalune, SylphraL ★ |
| Mont Rocheux | Gris | 18% | Bavoir, BraseoL ★ |
| Océan Bleu | Bleu | 12% | Dragodash, PyraflinL ★ |
| Grotte Sombre | Gris foncé | 22% | Skelerat, KarionLR ★ |
| Ciel Étoilé | Bleu clair | 8% | Cendralis, AuredrisL ★ |
| Ville | Blanc | 0% | — Champions d'Arène — |

★ = Légendaire

---

## ⚔️ Système de combat

### Calcul des dégâts
```
Dégâts bruts  = Attaque attaquant × Multiplicateur de type
Dégâts réels  = max(1, Dégâts bruts − Défense défenseur)
```

- **Coup critique** : 10% de chance → dégâts ×1.5
- **Attaque spéciale** : 50% de chance → dégâts ×2
- **Rate** : 10% de chance de manquer

### Champions (6v6)
Les champions envoient automatiquement leur Pokémon suivant quand l'actif tombe.
Le joueur doit choisir son remplaçant manuellement.



**Forme Ultime** : disponible à partir du niveau 30 — remet le Pokémon au niveau 5 avec des stats de base ×1.8.

---

## 💾 Sauvegarde

La sauvegarde est stockée dans `save_game.json` à la racine du projet :
- Position du joueur
- Équipe complète (PV actuels, stats, expérience)
- Réserve
- Inventaire (potions, pokéballs)

---

## 👥 Auteurs

Projet réalisé dans le cadre d'un cours de programmation Python.

---

## 📄 Licence

Projet éducatif — non affilié à Nintendo ou The Pokémon Company.
