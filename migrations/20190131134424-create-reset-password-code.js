'use strict';
module.exports = {
  up: (queryInterface, Sequelize) => {
    return queryInterface.createTable('ResetPasswordCodes', {
      id: {
        allowNull: false,
        autoIncrement: true,
        primaryKey: true,
        type: Sequelize.INTEGER
      },
      UserId: {
        type: Sequelize.INTEGER,
        onDelete: "CASCADE",
        allowNull: false,
        references: {
            model: 'Users',
            key: 'id'
        }
      },
      code: {
        type: Sequelize.STRING,
        allowNull: false
      },
      status: {
        type : Sequelize.ENUM('active', 'inactive', 'used', 'expired') ,
        allowNull : false,
        defaultValue: 'active'
      },
      createdAt: {
        allowNull: false,
        type: Sequelize.DATE
      },
      updatedAt: {
        allowNull: false,
        type: Sequelize.DATE
      }
    },
    {
        indexes: [
            {
                unique: true,
                fields: ['code']
            }
        ]
    });
  },
  down: (queryInterface, Sequelize) => {
    return queryInterface.dropTable('ResetPasswordCodes');
  }
};