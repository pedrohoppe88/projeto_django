
Cypress.Commands.add('login', (email, password) => {
  cy.visit('/usuarios/login/')
  cy.get('input[name="email"]').type(email)
  cy.get('input[name="senha"]').type(password)
  cy.get('form').submit()
})
