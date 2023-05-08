import tweepy
import json
import requests
import time
from datetime import datetime, timedelta, timezone

# Charger les informations de configuration à partir du fichier de configuration
with open('config.json') as f:
    config = json.load(f)

twitter_config = config['twitter']
telegram_config = config['telegram']

# Authentification à l'API Twitter
auth = tweepy.OAuth1UserHandler(
    consumer_key=twitter_config['consumer_key'],
    consumer_secret=twitter_config['consumer_secret'],
    access_token=twitter_config['access_token'],
    access_token_secret=twitter_config['access_token_secret']
)

# Création de l'objet API Twitter
api = tweepy.API(auth)

# Initialisation de la liste des tweets
tweets = []

# Boucle infinie
while True:
    # Récupération des 5 derniers tweets d'Elon Musk contenant les mots clés définis dans config.json
    new_tweets = api.user_timeline(screen_name=twitter_config['screen_name'], count=5)

    # Parcourir chaque nouveau tweet
    for tweet in new_tweets:
        # Vérifier si le tweet contient l'un des mots clés
        if any(keyword in tweet.text.lower() for keyword in twitter_config['keywords']):
            # Convertir la date et l'heure du tweet en format datetime avec le fuseau horaire UTC
            tweet_datetime = tweet.created_at.replace(tzinfo=timezone.utc).astimezone(tz=None)
            now = datetime.now(tz=timezone.utc).astimezone(tz=None)
            # Vérifier si le tweet est plus récent que l'intervalle de temps défini
            if now - tweet_datetime < timedelta(seconds=config['interval_seconds']):
                # Vérifier si le tweet n'a pas déjà été traité
                if tweet.id not in [t.id for t in tweets]:
                    # Ajouter le tweet à la liste des tweets
                    tweets.append(tweet)
                    # Ajouter un lien URL vers le tweet
                    tweet_url = f"https://twitter.com/{tweet.user.screen_name}/status/{tweet.id_str}"
                    # Ajouter une ligne vide entre les tweets
                    message = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] - {tweet.text}\n{tweet_url}\n"
                    print(message)
                    # Envoyer le tweet sur Telegram
                    params = {
                        'chat_id': telegram_config['chat_id'],
                        'text': message
                    }
                    response = requests.post(f"https://api.telegram.org/bot{telegram_config['token']}/sendMessage", data=params)
                    if response.ok:
                        print('Message envoyé avec succès sur Telegram!')
                    else:
                        print(f'Erreur lors de l\'envoi du message sur Telegram: {response.status_code} - {response.reason}')

    # Attendre l'intervalle de temps défini avant de vérifier à nouveau les tweets
    interval_seconds = config['interval_seconds']
    print(f"En attente de {interval_seconds} secondes...")
    time.sleep(interval_seconds)
