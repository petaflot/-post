# ⨯post

`⨯post` est un outil pour vous aider à rester propriétaire de vos données et a été conçu pour deux cas d'utilisation en particulier:
* vous remplissez un formulaire de contact sur une page web, mais le site ne vous transmet pas d'email avec la copie de votre demande ; généralement (et surtout lorsque celle-ci reste sans réponse), toute l'information est perdue (y compris le texte evoyé, mais aussi la date, l'heure..)
* vous postez un commentaire sur un site (par exemple youtube, facebook...), le commentaire est d'abord accepté mais vous vous apercez par la suite qu'il a été censuré : déjà que vous avez fait attention à rester politiquement, vous n'avez plus les détails pour comprendre et il vous faut recommencer depuis le début

## Fonctionnement

`⨯post` crée un [serveur proxy](https://fr.wikipedia.org/wiki/Proxy) par lequel transite votre traffic Internet ; pour des raisons de confidentialité et de performance, ce proxy est **local** (sur votre machine ou réseau local). Ce composant de `⨯post` (qui est est **libre, gratuit et open-source**) dispose d'une interface simple qui vous permet de:
* consulter les données que vous avez envoyé à des tiers
* gérer le filtrage de ces données (ie. ignorer certains sites) et ce qui est enregistré (par défaut les mots de passe ne sont pas enregistrés, les numéros de téléphone sont obfusqués)
* selon la configuration, `⨯post` peut faire office d'historique de navigation (particulièrement utile si vous utilisez le même proxy pour plusieurs clients)
* publier tout ou partie d'un post sur `⨯post.com`, de manière publique ou semi-privée, en indiquant la raison de la re-publication (par exemple "ce contenu a été censuré"). La re-publication est soumise à un abonnement à prix libre (montant minimum pour couvrir les frais: 7$/an, soit moins de 2ct./jour) ; à tout moment, vous pouvez choisir d'effacer la copie de vos commentaires.

À terme, `⨯post` peut servir à établir des statistiques sur les sites qui censurent le contenu des utilisateurs, ainsi que sur la part du contenu qui a causé la censure.
