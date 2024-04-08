#!/usr/bin/env python

# Testando minha primeira rede no mininet-wifi

import sys

from mininet.log import setLogLevel, info
from mn_wifi.cli import CLI
from mn_wifi.net import Mininet_wifi

def topology():
    # Cria uma rede
    net = Mininet_wifi()

    info(" *** Nós sendo criados ***\n")
    sta_arg, ap_arg = {}, {}
    if '-v' in sys.argv:
        sta_arg = {'nvif': 2}
    else:
        # isolate_clientes: Client isolation can be used to prevent low-level
        # bridging of frames between associated stations in the BSS.
        # By default, this bridging is allowed.
        # OpenFlow rules are required to allow communication among nodes
        ap_arg = {'client_isolation': True}

    # Criando access point (ponto de acesso)
    # wlans: significa a quantidade de interfaces wireless que serão criadas.
    # ssid: nome da wlan.
    # mode: IEEE 802.11a,b,g,b,p,ax,ac, etc.
    ap1 = net.addAccessPoint("ap1", wlans=1, ssid="net_yuri", mode="g", channel="5")

    # Criando stations (estações)
    # wlans: significa a quantidade de interfaces wireless que serão criadas.
    sta1 = net.addStation('sta1', wlans=1)
    sta2 = net.addStation('sta2', wlans=1)

    # Criando controlador
    c0 = net.addController('c0')

    info(" *** Nós sendo configurados ***\n")
    net.configureNodes()

    info(" *** Associando estações ***\n")
    # Colocando links
    net.addLink(sta1, ap1)
    net.addLink(sta2, ap1)
    
    info(" *** Iniciando rede ***\n")
    net.build()
    c0.start()
    ap1.start([c0])

    # ovs-ofctl é uma ferramenta de linha de comando que permite configurar switches OpenFlow
    # add-flow é um subcomando do ovs-ofctl que instrui o switch OpenFlow a adicionar uma nova regra de fluxo.
    # priority=0: Define a prioridade da regra. Neste caso, é definida como 0, o que significa que essa regra terá a menor prioridade e será aplicada por último, após todas as outras regras.
    # in_port=1: Define a porta de entrada na qual os pacotes devem chegar para corresponder à regra. Neste caso, é a porta 1 do ponto de acesso ap1.
    # actions=output:in_port,normal: Especifica as ações a serem tomadas quando um pacote corresponder à regra.
    # output:in_port: Isso instrui o switch OpenFlow a enviar o pacote de volta pela mesma porta de entrada. Em outras palavras, o pacote será enviado de volta para a interface que o recebeu originalmente.
    # normal: Isso indica que o pacote deve ser processado normalmente após ser enviado de volta pela mesma porta de entrada. No contexto do OpenFlow, normal significa que o switch deve encaminhar o pacote usando o encaminhamento padrão, sem aplicar regras adicionais de fluxo.

    if '-v' not in sys.argv:
        ap1.cmd('ovs-ofctl add-flow ap1 "priority=0,arp,in_port=1,'
                'actions=output:in_port,normal"')
        ap1.cmd('ovs-ofctl add-flow ap1 "priority=0,icmp,in_port=1,'
                'actions=output:in_port,normal"')
        ap1.cmd('ovs-ofctl add-flow ap1 "priority=0,udp,in_port=1,'
                'actions=output:in_port,normal"')
        ap1.cmd('ovs-ofctl add-flow ap1 "priority=0,tcp,in_port=1,'
                'actions=output:in_port,normal"')

    info(" *** Rodando CLI ***\n")
    CLI(net)

    info(" *** Parando Rede ***\n")
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    topology()
