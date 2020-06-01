'use strict';

module.exports = {
  up: (queryInterface, Sequelize) => {
    return queryInterface.addColumn('Users', 'temp_dotId', {
      type : Sequelize.STRING,
      allowNull : true,
    });
  },

  down: (queryInterface, Sequelize) => {
    return queryInterface.removeColumn('Users', 'temp_dotId');
  }
};
