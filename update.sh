# updates
python3 ./corona_charts.py -v California -n ca deaths
python3 ./corona_charts.py -v California -n ca confirmed
python3 ./corona_charts.py -v 'New York' -n ny deaths
python3 ./corona_charts.py -v 'New York' -n ny confirmed
python3 ./corona_charts.py -v Washington -n wa deaths
python3 ./corona_charts.py -v Washington -n wa confirmed
mv ./*.svg ./diagrams