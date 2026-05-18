[sre_nodes]
%{ for n in nodes ~}
${n.name} ansible_host=${n.ip} ansible_user=${ssh_user}
%{ endfor ~}

[monitoring]
${nodes[0].name} ansible_host=${nodes[0].ip} ansible_user=${ssh_user}
