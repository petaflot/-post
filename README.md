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


## Installation

### Local proxy

* call `./run.sh` in the project root
* Configure your browser to use 127.0.0.1:8080 as HTTP and HTTPS proxy
* Go to http://mitm.it and download the certificate (it is generated locally)
* Install certificate:
    * Firefox: Settings → Privacy & Security → Certificates → View Certificates → Authorities → Import
    * Chrome / system-wide:
        * macOS: add to Keychain and mark as “Always Trust”
        * Linux: place in /usr/local/share/ca-certificates/ and run update-ca-certificates
        * Windows: import into “Trusted Root Certification Authorities”
* Visit http://localhost:12345/ to view your post history and do the chosen action (delete, re-publish, etc..)
    * Use http://your.ip.address:12345/test to verify everything works as expected (caveat: some browsers like Firefox do not use the configured proxy for local addresses)

### Alterntaive: browser extension

* call `./run.sh` in the project root
* visit http://172.16.100.11:12345/about for further instructions

Note: this is untested!

## Structure du projet
```
xpot/
├── app/
│   ├── __init__.py
│   ├── main.py          # Quart app entrypoint
│   ├── db.py            # DB + writer
│   ├── ingest.py        # websocket ingestion
│   ├── api.py           # HTTP routes
│   ├── stream.py        # WS broadcast
│   └── templates/
│       ├── index.html
│       └── post.html
│
├── proxy/
│   ├── config.json      # filters by protocol, URL, field name ; obfuscation parameters
│   └── gather.py        # mitmproxy script
│
├── data/
│   └── traffic.db
│
├── requirements.txt
└── run.sh
```

## TODO

* per-URL fieldname regex rules ; problem with current field name and content rules (ie. passwords are saved)
* shared regex lists (similar to piHole)
* authentication
* `republish`
* `report` (we can't really expect the end-user to tweak a regex and form rules)
* delay-post: très utile si on est susceptible de poster des messages dans un état second (par exemple en étant alcoolisé) et qu'on pourrait regretter
