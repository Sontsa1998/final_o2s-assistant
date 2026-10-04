---
title: Performance
corpus: aide_en_ligne
source_format: markdown
source_url: https://o2s-help.harvest.fr/performance/
products:
- O2S
language: fr
audience: conseiller
audiences:
- conseiller
internal_links:
- https://o2s-help.harvest.fr/comparatif-entre-gain-brut-plus-value-et-performance/
doc_id: aide-171-performance
wp_post_id: 171
wp_categories:
- '89'
wp_statut: publish
thematique: O2S
date_modification: '2026-09-14'
---

## Sommaire

- Présentation
- Différents indicateurs de la performance en mode expert
- Méthode WCF
- Méthode Dietz
- Méthode TWR
- Taux de Rendement Interne (TRI)

## Présentation

Cette rubrique présente les différentes méthodes utilisées par O2S pour le calcul de la performance des supports du portefeuille. Cette fonctionnalité est accessible depuis Services > Modules > Portefeuille > Calculs de la performance de l’application O2S. performance des supports du portefeuille Services > Modules > Portefeuille > Calculs de la performance Les calculs réalisés dans O2S sont directement liés aux supports investis dans le contrat. Voici les principales notions à comprendre pour une analyse précise des données : Plus-value / Moins-value.

### Plus-value / Moins-value

La notion de plus-value ou moins-value repose sur le prix moyen d’achat des supports. Ces prix moyens peuvent être : prix moyen d’achat Poussés automatiquement par vos partenaires via l’agrégation.

### Poussés automatiquement par vos partenaires via l’agrégation

Non poussés, auquel cas ils ne seront pas pris en compte dans les calculs. Pour vérifier si vos partenaires transmettent bien les prix moyens d’achat, nous vous recommandons de consulter les caractéristiques des partenaires interfacés dans O2S. Cela vous permettra d’évaluer l’impact de ces données sur vos analyses. caractéristiques des partenaires interfacés dans O2S Gains. La notion de gains est directement liée aux mouvements (versements, retraits, arbitrages, etc.) effectués sur les contrats. Pour garantir la fiabilité des calculs, il est essentiel que vos partenaires transmettent correctement ces mouvements dans O2S. Nous vous invitons à vérifier la qualité et la complétude des données transmises par vos partenaires pour éviter toute incohérence dans les résultats. mouvements En résumé, une bonne compréhension et une vérification régulière des données transmises par vos partenaires sont indispensables pour exploiter pleinement les fonctionnalités d’O2S et fournir des analyses fiables à vos clients.

### Mesures de la performance

Trois modes d’utilisation sont disponibles pour effectuer la mesure de la performance : le mode WCF (sélectionné par défaut), le mode standard et le mode expert. Le mode WCF permet d’obtenir des résultats en utilisant une mesure de la performance qui fonctionne même quand les informations sur les mouvements sont bien, mal ou non renseignées; le mode standard présente les résultats du calcul de performance selon une seule méthode (jugée comme la plus pertinente dans le contexte du compte étudié); tandis que le mode expert effectue cette opération en utilisant jusqu’à 3 méthodes de calculs (certaines méthodes étant plus adaptées aux différents contextes rencontrés). le mode WCF (sélectionné par défaut), le mode standard et le mode expert.

Enfin, une dernière méthode, permet d’exprimer la rentabilité d’un placement financier via le calcul du Taux de Rendement Interne. Grâce à l’évolution historique des comptes constituant le portefeuille de votre client, vous pourrez mieux appréhender l’évolution future des avoirs de vos clients. Par défaut, c’est le mode standard qui est retenu lors de l’installation du logiciel pour chaque utilisateur. Si vous souhaitez disposer du mode expert, cliquez sur Services > Modules > Portefeuille > Calculs de la performance, puis dans la zone « Mode de calcul de la performance », sélectionnez Mode expert à l’aide de la liste déroulante. Si vous ne souhaitez disposer que de la méthode WCF, sélectionnez-la également à l’aide de cette liste déroulante.

Différents indicateurs de la performance en mode expert.

## Différents indicateurs de la performance en mode expert

Trois méthodes de calcul ont été mises en œuvre afin de fiabiliser les résultats. Une mesure de la performance sans dynamique de flux (méthode WCF). Cette méthode part du principe que les mouvements de flux de trésorerie, associés à la valorisation d’un compte, ne sont pas fréquemment disponibles en import et s’ils sont renseignés manuellement, ne sont pas datés avec précision. En effet, la saisie manuelle est possible en l’absence de mouvements importés, mais cette saisie reste source d’erreurs. Dans certains cas, la saisie d’un flux avec un écart d’un jour peut fausser l’estimation de la performance des supports de l’investissement. Le pire des cas de figures, et sans doute le plus fréquent, correspond à celui où aucun flux n’est renseigné.

Il est alors impossible de faire la distinction entre le rendement lié à la performance du sous-jacent et celui, largement fictif, consécutif à un mouvement de trésorerie. Compte tenu de ces écueils prévisibles, nous avons mis en œuvre une méthode d’estimation de la performance qui n’est pas tributaire des flux. Cette méthode fonctionne donc, que les flux soient bien, mal ou non renseignés. Plus précisément, il s’agit d’estimer la performance d’un placement à partir de celle des supports d’investissement et de la valeur des lignes du portefeuille. Ces dernières vont permettre de calculer la ventilation du portefeuille par produit et d’en tirer une pondération qui, appliquée aux historiques de rendements des supports, contribuera à personnaliser le calcul de la performance.

Dans cette démarche les éventuels flux de trésorerie sont intégrés dans les valorisations des différentes lignes du portefeuille et permettent de suivre l’évolution de la structure des poids du portefeuille (cf. exemple proposé à la fin de cette note). Une mesure de la performance avec flux de trésorerie (méthode de Dietz). Cette méthode connue sous le nom de méthode de Dietz modifiée, fait partie de la famille des « Money Weighted Rate of Return ». Cette méthode requiert une information précise sur la date des achats/retraits. Dans le cas contraire, les performances calculées peuvent être gravement faussées. Il s’agit d’une approximation du Taux de Rendement Interne. Elle consiste à mesurer une performance en tenant compte de la date et du montant des flux de trésorerie.

Les résultats qu’elle détermine reflètent donc la performance des supports et celle du gérant. Le calcul ne nécessite pas de connaître la valorisation d’un portefeuille à la date de chaque flux de trésorerie. La technique est donc largement utilisée en raison de son caractère parcimonieux. Une mesure de la performance neutralisant l’effet des flux de trésorerie (méthode TWR). La méthode des Rendements pondérés par le temps, considérée par beaucoup comme la méthode « idéale », fait partie de la lignée des « Time Weighted Rate of Return ». C’est la méthode la plus exacte pour calculer les rendements d’un placement comparée aux autres méthodes d’approximation (Dietz; WCF). Elle permet d’éliminer l’effet perturbateur des flux sur la performance.

Elle reflète donc la performance des supports d’investissement tout en tenant compte de l’incidence des frais et autres chargements sur la performance. Cette méthode est relativement exigeante et nécessite en théorie une valorisation journalière des portefeuilles. Cette contrainte peut être partiellement relaxée, néanmoins la moindre erreur dans le renseignement des flux peut conduire, comme pour la méthode de Dietz, à mesurer des performances aberrantes.

## Méthode WCF

On peut facilement illustrer la méthode avec un compte constitué de deux OPCVM fictifs : Cardinal Evolution Cardinal Patrimoine Cardinal Evolution Cardinal Patrimoine Pour une date de cotation donnée (ici le 15/09/2008), on dispose de la valorisation par support. On en déduit immédiatement qu’à cet instant, le portefeuille a la pondération suivante : Cardinal Evolution : 16.60% Cardinal Patrimoine : 100.00% Patrimoine : 83.40% __________ 100.00% Cardinal Evolution : 16.60% Cardinal Evolution : Cardinal Evolution : 16.60% 16.60% Cardinal Patrimoine : 83.40% Cardinal Patrimoine : Cardinal Patrimoine : 83.40% 83.40% __________ La base de données qui alimente l’application O2S contient l’historique des performances des fonds constitutifs du compte que nous étudions.

Imaginons que les rendements des fonds Cardinal Evolution et Cardinal Patrimoine soient respectivement de 0.50% et -0.20% au 15/09/2008. Il est alors élémentaire d’estimer la performance du portefeuille à cette date : (0.50%*16.60%) + (-0.20%*83.40%) = -0.08% (0.50%*16.60%) + (-0.20%*83.40%) = -0.08% L’historique des valorisations par support est stocké dans la base de données de l’application O2S, il est donc possible de calculer la performance des supports du compte depuis son existence dans l’application. Les arbitrages entre les fonds, les flux de trésorerie ainsi que le différentiel de rendement entre Cardinal Evolution et Cardinal Patrimoine vont impacter les valorisations et contribuer à déformer graduellement la structure du compte.

Le calcul de la performance est donc individualisé et prend en compte l’évolution des poids relatifs des supports d’investissement. A l’instar de la seconde mesure de la performance, cette méthode simple et robuste reflète la performance du portefeuille hors influence des mouvements de trésorerie. La limite de la formule est qu’elle ne prend pas en compte l’impact des frais (de souscription, de transaction, droits de garde.) sur la performance.

## Taux de Rendement Interne (TRI)

Interne) qui exprime la rentabilité d’un placement financier sur une période donnée. Concept. TRI prend en compte les versements et les retraits successifs ainsi que la valeur liquidative du compte à la date du calcul. Contrairement aux méthodes du type TWR (Time Weighted Rate of Return) qui permettent d’éliminer l’effet perturbateur des flux sur la performance, le TRI est sensible aux montants des Cash Flows. Le TRI reflète donc, pour partie, l’efficacité de la stratégie de gestion déterminée par le calendrier des flux de trésorerie (timing of cash flows). Lorsque le TRI d’un investissement est supérieur au rendement moyen de ses sous-jacents hors Cash Flows (cf. méthodes TWR, Dietz et WCF dans O2S) cela signifie, le cas échéant, que les retraits ont eu tendance à être effectués en haut de cycle et les versements en bas de cycle.

Formellement, dans le cas de la mesure de la performance d’un investissement, le TRI est le taux qui annule la valeur capitalisée d’une série de flux financiers. Avec : CF = Cash Flows TRI = Taux de rendement interne I = Valeur capitalisée de fin de période La solution du problème revient à chercher les racines d’un polynôme. Dans cette méthode, les racines du polynôme sont calculées à partir de la méthode des matrices de « frobenius » ou « matrices compagnons ». Les valeurs propres réelles de la matrice compagnon sont les racines du polynôme constitué par la séquence des cash flows. Le calcul du gain brut permet de guider la sélection dans le cas de racines réelles multiples.

### Mise en œuvre

Dans O2S, le Taux de Rendement Interne figure sur les tableaux d’évolution des comptes du module Contacts > Portefeuille > Comptes. TRI n’est pas présent dans les tableaux d’évolution comptes. Si vous souhaitez en disposer, allez dans Services > Modules > Portefeuille > Portefeuille et comptes (1/2), puis au niveau de Afficher dans le tableau de l’évolution du compte et du portefeuille la performance de type TRI/TWR/WCF/Dietz, sélectionnez TRI. Pour en savoir plus… Comparatif entre le gain brut, la plus-value et la performance Pour en savoir plus…

| 83.40% __________ 100.00% Cardinal Evolution: | 16.60 |
|---|---|
| Cardinal Patrimoine: | 83.40 |
