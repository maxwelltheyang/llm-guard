# Ensure to update the IP for SSH ingress as needed, do not leave 0.0.0.0/0
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: ssh-ingress-policy
spec:
  podSelector:
    matchLabels:
      app: my-app
  ingress:
  - ports:
    - containerPort: 22
      protocol: tcp
      ipBlock:
        cidr: 10.0.1.100/32 # Update this IP to the actual SSH client's IP address
