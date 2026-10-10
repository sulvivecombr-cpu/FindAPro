"""Legal documents (platform content, not user data): Terms, Privacy, Data
Providers, Software License, Location — Brazil-first, LGPD-aligned."""
from django.db import migrations

DOCUMENTS = [
    ('termos', 'Termos de Uso do FindAPro', (
        'Última atualização: 10/10/2026\n\n'
        '1. OBJETO\n'
        'O FindAPro é uma plataforma digital brasileira que conecta clientes e profissionais '
        'autônomos, MEIs e empresas para a contratação de serviços locais e digitais. Estes '
        'Termos regulam o uso da plataforma por visitantes, clientes e profissionais.\n\n'
        '2. ACEITAÇÃO\n'
        'Ao criar uma conta, você declara ter lido e aceito integralmente estes Termos e a '
        'Política de Privacidade. O uso da plataforma sem conta está sujeito às mesmas regras.\n\n'
        '3. CONTAS E PAPÉIS\n'
        '3.1. Cliente: pessoa física (CPF) ou jurídica (CNPJ) que contrata serviços.\n'
        '3.2. Profissional: pessoa autônoma (CPF), MEI ou empresa (CNPJ) que oferece serviços.\n'
        '3.3. É vedada a criação de contas duplicadas, o uso de dados de terceiros sem '
        'autorização e o fornecimento de informações falsas.\n\n'
        '4. CONDUTA\n'
        'São proibidos: assédio, discriminação, anúncios e conteúdos ilícitos ou enganosos, '
        'burla do sistema de pagamentos da plataforma, uso de robôs ou scraping e qualquer '
        'prática que viole a legislação brasileira, incluindo o Marco Civil da Internet (Lei '
        '12.965/2014) e o Código de Defesa do Consumidor.\n\n'
        '5. PAGAMENTOS E REPASSES\n'
        'Os pagamentos por serviços contratados dentro do app serão processados por '
        'prestadores de pagamento identificados na própria contratação. Tarifas e prazos de '
        'repasse serão informados no momento de cada transação.\n\n'
        '6. RESPONSABILIDADES\n'
        'O FindAPro atua como intermediador da relação entre cliente e profissional, '
        'fornecendo estrutura de contato, agendamento e pagamento. A execução técnica do '
        'serviço é de responsabilidade do profissional contratado.\n\n'
        '7. SUSPENSÃO E ENCERRAMENTO\n'
        'O FindAPro pode suspender ou encerrar contas que violem estes Termos. Você pode '
        'encerrar sua conta a qualquer momento, exercendo o direito de eliminação previsto '
        'na LGPD, em Configurações > Conta > Excluir conta.\n\n'
        '8. LEGISLAÇÃO APLICÁVEL\n'
        'Estes Termos são regidos pelas leis da República Federativa do Brasil, incluindo a '
        'LGPD (Lei 13.709/2018) e o Marco Civil da Internet.\n'
    )),
    ('privacidade', 'Política de Privacidade (LGPD)', (
        'Última atualização: 10/10/2026\n\n'
        '1. QUEM SOMOS\n'
        'O FindAPro trata dados pessoais como controlador, em conformidade com a Lei Geral '
        'de Proteção de Dados — LGPD (Lei 13.709/2018).\n\n'
        '2. DADOS QUE TRATAMOS\n'
        '2.1. Dados de cadastro: nome, e-mail, senha (armazenada apenas como hash), tipo de '
        'conta e idioma.\n'
        '2.2. Consentimentos: tipo, versão do documento, data/hora, endereço IP e navegador.\n'
        '2.3. Dados de uso e segurança: registros de auditoria (ação, entidade, data/hora, IP '
        'e dispositivo).\n'
        '2.4. Dados de endereço e localização: usados para buscar profissionais próximos.\n\n'
        '3. FINALIDADES E BASE LEGAL\n'
        'Tratamos seus dados para: executar o contrato de uso da plataforma (execução de '
        'contrato), cumprir obrigações legais (obrigação legal), melhorar o serviço e '
        'garantir a segurança (legítimo interesse) e enviar comunicações essenciais '
        '(execução de contrato).\n\n'
        '4. COMPARTIMENTAÇÃO\n'
        'Seus dados não são vendidos. Podem ser compartilhados com: prestadores de '
        'pagamento (quando a fase de pagamentos for ativada), provedores de dados públicos '
        'listados no documento "Provedores de Dados" e autoridades, quando exigido por lei.\n\n'
        '5. SEUS DIREITOS (ART. 18 DA LGPD)\n'
        'Você pode: confirmar a existência de tratamento, acessar seus dados, corrigir '
        'dados incompletos ou desatualizados, solicitar a portabilidade, obter informação '
        'sobre compartilhamento, revogar consentimentos e solicitar a eliminação de dados '
        'pessoais. A exclusão de conta está disponível em Configurações > Conta > Excluir '
        'conta.\n\n'
        '6. RETENÇÃO E ELIMINAÇÃO\n'
        'Os registros de consentimento e auditoria são mantidos pelo prazo legal mínimo '
        'para fins de defesa em processos; os demais dados pessoais são eliminados ou '
        'anonimizados quando você solicita a exclusão da conta.\n\n'
        '7. SEGURANÇA\n'
        'Aplicamos medidas técnicas e administrativas para proteger seus dados, incluindo '
        'criptografia de senha, trilha de auditoria imutável e controle de acesso por '
        'papel (row-level security no modelo de dados).\n'
    )),
    ('provedores-dados', 'Provedores de Dados', (
        'Última atualização: 10/10/2026\n\n'
        'O FindAPro utiliza dados públicos das seguintes fontes oficiais para preencher '
        'endereços e localidades:\n\n'
        '1. IBGE — Instituto Brasileiro de Geografia e Estatística\n'
        'API pública (servicodados.ibge.gov.br) para lista oficial de estados e municípios '
        'do Brasil, usada nos seletores de cidade e estado.\n\n'
        '2. Correios\n'
        'Base de Códigos de Endereçamento Postal (CEP) para preenchimento automático de '
        'endereço a partir do CEP informado.\n\n'
        '3. Google\n'
        'Login com Google (OAuth 2.0): quando você usa "Continuar com Google", recebemos '
        'seu nome, e-mail e foto de perfil, conforme autorizado por você na tela do Google.\n\n'
        'Estes provedores só recebem os dados mínimos necessários. Nenhum dado pessoal seu '
        'é enviado ao IBGE ou aos Correios: as consultas usam apenas CEP ou localidade.'
    )),
    ('licenca-software', 'Licença de Software', (
        'Última atualização: 10/10/2026\n\n'
        '1. LICENÇA DE USO\n'
        'O FindAPro concede a você uma licença pessoal, limitada, revogável e não '
        'exclusiva para acessar e usar a plataforma conforme estes termos.\n\n'
        '2. PROPRIEDADE INTELECTUAL\n'
        'A plataforma, incluindo código-fonte, interface, logotipo e marca FindAPro, é '
        'protegida pela Lei 9.610/1998 (Lei de Direitos Autorais) e pela Lei da Propriedade '
        'Industrial (Lei 9.279/1996). É vedada a cópia, engenharia reversa ou exploração '
        'comercial não autorizada.\n\n'
        '3. SOFTWARE DE TERCEIROS\n'
        'A plataforma utiliza software de terceiros sob licenças abertas (por exemplo, '
        'Django sob a licença BSD de 3 cláusulas e Tailwind CSS sob a licença MIT), cujos '
        'avisos de copyright são mantidos nos créditos do projeto.\n\n'
        '4. CONTEÚDO DOS USUÁRIOS\n'
        'Você mantém a propriedade do conteúdo que publica (fotos, descrições e avaliações) '
        'e concede ao FindAPro licença para exibi-lo dentro da plataforma enquanto sua '
        'conta estiver ativa.'
    )),
    ('localizacao', 'Uso de Localização', (
        'Última atualização: 10/10/2026\n\n'
        '1. PARA QUE USAMOS LOCALIZAÇÃO\n'
        'A localização é usada para mostrar profissionais e serviços próximos a você, '
        'preencher endereços (via CEP dos Correios e cidades do IBGE) e calcular distâncias '
        'de atendimento.\n\n'
        '2. CONTROLE\n'
        'Você define manualmente sua cidade e CEP no perfil. A permissão de localização do '
        'navegador é opcional e pode ser revogada a qualquer momento nas configurações do '
        'navegador.\n\n'
        '3. RETENÇÃO\n'
        'Os dados de localização informados por você ficam vinculados à sua conta e são '
        'eliminados quando você solicita a exclusão da conta (LGPD, art. 18, VI).'
    )),
]


def create_documents(apps, schema_editor):
    LegalDocument = apps.get_model('foundation', 'LegalDocument')
    for doc_type, title, content in DOCUMENTS:
        LegalDocument.objects.get_or_create(
            doc_type=doc_type,
            version='1.0',
            defaults={'title': title, 'content': content, 'is_current': True},
        )


def remove_documents(apps, schema_editor):
    LegalDocument = apps.get_model('foundation', 'LegalDocument')
    LegalDocument.objects.filter(doc_type__in=[d[0] for d in DOCUMENTS], version='1.0').delete()


class Migration(migrations.Migration):
    dependencies = [
        ('foundation', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_documents, remove_documents),
    ]
