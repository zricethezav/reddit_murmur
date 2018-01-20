# PG 10 install and setup
apt-get install -y postgresql

# create user
output=$(sudo -u postgres psql -c '\du' -A -F, -t | grep ${REDDIT_MURMUR_PG_USER})
return_code=$?
if [ $return_code -eq 0 ]; then
    echo "PostgreSQL User ${REDDIT_MURMUR_PG_USER} already exists."
else
    echo "Creating PostgreSQL user ${REDDIT_MURMUR_PG_USER}"
    sudo -u postgres psql -c "create role ${REDDIT_MURMUR_PG_USER} with superuser createdb login createrole password '${REDDIT_MURMUR_PG_PW}'";
fi

# create db
output=$(sudo -u postgres psql -c '\l' -A -F, -t | grep ${REDDIT_MURMUR_DB})
return_code=$?
if [ $return_code -eq 0 ]; then
    echo "Database ${REDDIT_MURMUR_DB} already exists."
else
    echo "Creating database ${REDDIT_MURMUR_DB} with owner ${REDDIT_MURMUR_PG_USER}"
    sudo -u postgres createdb ${REDDIT_MURMUR_DB} -O ${REDDIT_MURMUR_PG_USER}
fi

# enable trust for local host
sudo sed -i -e s/md5/trust/g /etc/postgresql/10/main/pg_hba.conf

service postgresql reload
