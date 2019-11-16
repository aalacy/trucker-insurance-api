'use strict';

module.exports = {
  up: (queryInterface, Sequelize) => {
    return queryInterface.createTable('Policy', {
      id: {
        allowNull: false,
        autoIncrement: true,
        primaryKey: true,
        type: Sequelize.INTEGER
      },
      broker_id: {
        type: Sequelize.INTEGER,
        allowNull:false
      },
      uuid: {
        type: Sequelize.STRING,
        allowNull:false
      },
      certificate_file: {
        type: Sequelize.STRING,
        allowNull:false
      },
      document_file: {
        type: Sequelize.STRING,
        allowNull:false
      }
    });
  },

  down: (queryInterface, Sequelize) => {
    return queryInterface.dropTable('Policy');

    /*
      Add reverting commands here.
      Return a promise to correctly handle asynchronicity.

      Example:
      return queryInterface.dropTable('users');
    */
  }
};
