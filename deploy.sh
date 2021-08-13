# deploy.sh

if [[ $# -eq 0 ]] ; then
    echo 'ERROR: arg $1 (ENV_FILE) not passed.';
    exit 1;
fi

ENV_FILE="$1";

# export deploy env vars
export $(grep -e 'DEPLOY' $ENV_FILE | xargs)

# activate virtual env
source $DEPLOY_ENV_DIR/bin/activate
echo "Activated virtualenv - $(which python)"

# pull master branch
cd $DEPLOY_PROJECT_DIR || { exit 1; }
git pull origin master

# run django commands
python manage.py migrate
python manage.py collectstatic --link --noinput
python manage.py makemessages --all

# restart web application
touch /etc/uwsgi-emperor/vassals/$DEPLOY_UWSGI_INI_FILE
##
