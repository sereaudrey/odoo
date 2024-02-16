# Activer l'environnement virtuel
source ./venv/Scripts/activate

# Lancer odoo
python ./odoo-bin -r odoo -w admin --addons-path="./addons,./addons_dev" 