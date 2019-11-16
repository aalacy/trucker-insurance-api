let models = require("../models/auto")
let md5 = require("md5")

// load all the things we need
let LocalStrategy = require('passport-local').Strategy
let FacebookTokenStrategy = require('passport-facebook-token')
const TwitterTokenStrategy = require('passport-twitter-token')

// expose this function to our app using module.exports
module.exports = function (passport) {
    passport.serializeUser(function (user, done) {
        done(null, user)
    })

    passport.deserializeUser(async (user, done) => {
        done(null, user)
        /*new models.User().findUser({id:user.id})
            .then((user) => {
                done(null, user)
            }).catch(err => {
            done(err, null)
        })*/
    })

    passport.use(new LocalStrategy({
            // by default, local strategy uses username and password, we will override with email
            usernameField: 'email',
            passwordField: 'password',
            passReqToCallback: true // allows us to pass back the entire request to the callback
        },
        function (req, email, password, done) {
            new models.User().login({
                email: email.toLowerCase(),
                password: md5(password)
            }).then(user => {
                if (user == null) {
                    return done(null, false)
                } else {
                    return done(null, user)
                }
            }).catch(err => {
                return done(err)
            })

        })
    )
/*
    passport.use(new FacebookTokenStrategy({
            clientID: "",
            clientSecret: "",
            accessTokenField: "token"
        },
        function (accessToken, refreshToken, profile, done) {
            // console.log(JSON.parse(profile._raw))
            new models.User().checkFacebook(JSON.parse(profile._raw)).then(user => {
                return done(null, user)
            }).catch(err => {
                return done(err)
            })
        }
    ))

    passport.use(new TwitterTokenStrategy({
            consumerKey: '',
            consumerSecret: '',
            oauthTokenField: "token",
            oauthTokenSecretField: "tokenSecret"
        }, (token, tokenSecret, profile, done) => {
            // console.log(profile)
            new models.User().checkTwitter(profile).then(user => {
                return done(null, user)
            }).catch(err => {
                return done(err)
            })
        }
    ))*/
}