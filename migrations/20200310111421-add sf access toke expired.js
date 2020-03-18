'use strict';

module.exports = {
  up: (queryInterface, Sequelize) => {
    return queryInterface.addColumn('Users', 'sf_token_expired', {
      type : Sequelize.DATE,
      allowNull : true,
    })
  },

  down: (queryInterface, Sequelize) => {
    return queryInterface.removeColumn('Users', 'sf_token_expired')
  }
};
