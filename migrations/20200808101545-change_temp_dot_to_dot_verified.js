'use strict';

module.exports = {
  up: (queryInterface, Sequelize) => {
    return Promise.all([
      queryInterface.removeColumn('Users', 'temp_dotId'),
      queryInterface.addColumn('Users', 'dot_verified', {
        type : Sequelize.BOOLEAN,
        allowNull : true,
      })
    ])
  },

  down: (queryInterface, Sequelize) => {
    return Promise.all([
      queryInterface.removeColumn('Users', 'dot_verified'),
      queryInterface.addColumn('Users', 'temp_dotId', {
        type : Sequelize.STRING,
        allowNull : true,
      })
    ])
  }
};
