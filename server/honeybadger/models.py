from honeybadger import db, bcrypt
from honeybadger.constants import ROLES, STATUSES
from honeybadger.utils import get_guid
import binascii
import datetime

def stringify_datetime(value):
    """Deserialize datetime object into string form for JSON processing."""
    if value is None:
        return None
    return value.strftime("%Y-%m-%d %H:%M:%S")

class Beacon(db.Model):
    __tablename__ = 'beacons'
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.DateTime, default=datetime.datetime.now)
    target_guid = db.Column(db.String, db.ForeignKey('targets.guid'), nullable=False)
    agent = db.Column(db.String)
    ip = db.Column(db.String)
    port = db.Column(db.String)
    useragent = db.Column(db.String)
    comment = db.Column(db.String)
    lat = db.Column(db.String)
    lng = db.Column(db.String)
    acc = db.Column(db.String)

    @property
    def serialized(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id,
            'time': stringify_datetime(self.time),
            'target': self.target.name,
            'agent': self.agent,
            'ip': self.ip,
            'port': self.port,
            'useragent': self.useragent,
            'comment': self.comment,
            'lat': self.lat,
            'lng': self.lng,
            'acc': self.acc,
        }

    def __repr__(self):
        return "<Beacon '{}'>".format(self.target.name)

class Target(db.Model):
    __tablename__ = 'targets'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    guid = db.Column(db.String, default=get_guid())
    owner = db.Column(db.String, db.ForeignKey('users.id'), nullable=False)
    beacons = db.relationship('Beacon', backref='target', lazy='dynamic')

    @property
    def beacon_count(self):
        return len(self.beacons.all())

    def __repr__(self):
        return "<Target '{}'>".format(self.name)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, nullable=False, unique=True)
    password_hash = db.Column(db.String)
    role = db.Column(db.Integer, nullable=False, default=1)
    status = db.Column(db.Integer, nullable=False, default=0)
    token = db.Column(db.String)
    targets = db.relationship('Target', backref='user', lazy='dynamic')

    @property
    def role_as_string(self):
        return ROLES[self.role]

    @property
    def status_as_string(self):
        return STATUSES[self.status]

    @property
    def password(self):
        raise AttributeError('password: write-only field')

    @password.setter
    def password(self, password):
        self.password_hash = bcrypt.generate_password_hash(binascii.hexlify(password))

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, binascii.hexlify(password))

    @property
    def is_admin(self):
        if self.role == 0:
            return True
        return False

    @staticmethod
    def get_by_email(email):
        return User.query.filter_by(email=email).first()

    def __repr__(self):
        return "<User '{}'>".format(self.email)
