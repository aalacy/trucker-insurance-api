'use strict';

module.exports = {
  up: (queryInterface, Sequelize) => {
    return Promise.all([
      queryInterface.addColumn('Companies', 'is_quote_modified', {
        type : Sequelize.BOOLEAN,
        allowNull : true,
        defaultValue: true
      }),
      queryInterface.addColumn('Companies', 'is_coi_modified', {
        type : Sequelize.BOOLEAN,
        allowNull : true,
        defaultValue: true
      }),
    ])
  },

  down: (queryInterface, Sequelize) => {
    return Promise.all([
      queryInterface.removeColumn('Companies', 'is_quote_modified'),
      queryInterface.removeColumn('Companies', 'is_coi_modified')
    ])
  }
};
