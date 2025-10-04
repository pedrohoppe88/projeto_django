describe('Testes de Usuário - Cadastro e Login', () => {
  it('Deve carregar a página de cadastro', () => {
    cy.visit('/usuarios/cadastrar/')
    cy.contains('Cadastro de Usuário')
  })

  it('Deve enviar formulário de cadastro com sucesso', () => {
    cy.visit('/usuarios/cadastrar/')
    cy.get('input[id="id_nome"]').type('Teste Cypress')
    cy.get('input[name="email"]').type('teste.cypress@example.com')
    cy.get('input[name="senha"]').type('senha123')
    cy.get('form').submit()
    cy.url().should('include', '/usuarios/login/')
  })

  it('Deve carregar a página de login', () => {
    cy.visit('/usuarios/login/')
    cy.contains('Login')
  })

  it('Deve fazer login com usuário cadastrado', () => {
    cy.visit('/usuarios/login/')
    cy.get('input[name="email"]').type('teste.cypress@example.com')
    cy.get('input[name="senha"]').type('senha123')
    cy.get('button').click()
  })
})
