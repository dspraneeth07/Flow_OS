FROM flowosai/flowos:1.0-alpha

CMD ["python", "-m", "flowos", "run", "--host", "0.0.0.0", "--port", "7860"]
