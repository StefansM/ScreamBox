"""
Datastore layout:

```
/users/$USER_ID
  webhook_key: $WEBHOOK_SECRET_KEY
  incidents:
    $PAGERDUTY_INCIDENT_KEY:
      state: $PAGERDUTY_STATUS

/webhooks/$WEBHOOK_SECRET_KEY
  id: $USER_ID
```

The `/webhooks` collection is only used when trying to register a new user. If the webhook secret key is already
present, then the existing user ID can be used. If the `/users` document was created when the webhook was registered,
it would be possible for two simultaneous requests to generate different user IDs and link two users to the same secret
key.

The `$PAGERDUTY_STATUS` and `$PAGERDUTY_INCIDENT_KEY` are passed by PagerDuty when it triggers this webhook.
"""
import uuid

from google.cloud import firestore

from screambox.model import Incident, OPEN_STATUSES


class Datastore:
    """Access and modify the incidents associated with a user."""
    def __init__(self, db: firestore.Client, user: str):
        self.db = db
        self.user_doc = db.collection("users").document(user)

        if not self.user_doc.get().exists:
            raise ValueError("User does not exist")

        self.incidents_coll = self.user_doc.collection("incidents")

    @staticmethod
    def _stream_to_incidents(stream) -> list[Incident]:
        return [Incident(i.reference.id, i.get("state")) for i in stream]

    def open_incidents(self) -> list[Incident]:
        stream = self.incidents_coll.where("state", "in", OPEN_STATUSES).stream()
        return self._stream_to_incidents(stream)

    def closed_incidents(self):
        stream = self.incidents_coll.where("state", "not-in", OPEN_STATUSES).stream()
        return self._stream_to_incidents(stream)

    def set_state(self, incident_key: str, state: str):
        self.incidents_coll.document(incident_key).set({"state": state})

    def delete_incident(self, incident_key: str):
        doc = self.incidents_coll.document(incident_key)
        doc.delete()


class Userstore:
    """
    The user store contains a mapping between user ID and webhook secret key.

    To register a user, pass the secret key associated with your PagerDuty webhook. The user store will atomically
    create a user identifier that is used to trigger and retrieve incidents associated with the webhook.
    """

    def __init__(self, db: firestore.Client):
        self.db = db
        self.users_coll = db.collection("users")
        self.webhooks_coll = db.collection("webhooks")

    def register(self, secret_key: str) -> str:
        """Register a user given a webhook key and return a new user identifier."""
        transaction = self.db.transaction()

        @firestore.transactional
        def _register_hook(txn, webhook):
            user_ref = self.webhooks_coll.document(webhook)
            existing_user = user_ref.get(transaction=txn)

            if not existing_user.exists:
                uid = str(uuid.uuid4())
                transaction.set(user_ref, {"id": uid})

        _register_hook(transaction, secret_key)
        user_id = self.webhooks_coll.document(secret_key).get().get("id")

        self.users_coll.document(user_id).set({"secret_key": secret_key})

        return user_id
