describe('Testes de Sessão - Criar e Listar', () => {
  beforeEach(() => {
    // Fazer login antes de cada teste
    cy.visit('/usuarios/login/')
    cy.get('input[name="email"]').type('teste.cypress@example.com')
    cy.get('input[name="senha"]').type('senha123')
    cy.get('form').submit()
  })

  it('Deve carregar a página de criar sessão', () => {
    cy.visit('/criar_sessao/')
    cy.contains('Criar Sessão')
  })

  it('Deve criar uma nova sessão', () => {
    cy.visit('/criar_sessao/')
    cy.get('input[name="nome"]').type('Sessão Teste Cypress')
    cy.get('input[name="senha"]').type('senha123')
    cy.get('form').submit()
    cy.url().should('include', '/listar_sessoes')
    cy.contains('Sessão Teste Cypress')
  })

  it('Deve listar sessões existentes', () => {
    cy.visit('/listar_sessoes/')
    cy.get('body').should('contain', 'Sessões Disponíveis')
  })
})
