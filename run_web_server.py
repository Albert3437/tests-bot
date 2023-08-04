import subprocess


subprocess.run('streamlit run web.py --theme.base "dark" --server.port 5001', shell=True, stdout=subprocess.PIPE)

