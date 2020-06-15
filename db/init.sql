BEGIN TRANSACTION;
INSERT INTO stone(val) VALUES ('0|0');
INSERT INTO stone(val) VALUES ('0|1');
INSERT INTO stone(val) VALUES ('0|2');
INSERT INTO stone(val) VALUES ('0|3');
INSERT INTO stone(val) VALUES ('0|4');
INSERT INTO stone(val) VALUES ('0|5');
INSERT INTO stone(val) VALUES ('0|6');
INSERT INTO stone(val) VALUES ('1|1');
INSERT INTO stone(val) VALUES ('1|2');
INSERT INTO stone(val) VALUES ('1|3');
INSERT INTO stone(val) VALUES ('1|4');
INSERT INTO stone(val) VALUES ('1|5');
INSERT INTO stone(val) VALUES ('1|6');
INSERT INTO stone(val) VALUES ('2|2');
INSERT INTO stone(val) VALUES ('2|3');
INSERT INTO stone(val) VALUES ('2|4');
INSERT INTO stone(val) VALUES ('2|5');
INSERT INTO stone(val) VALUES ('2|6');
INSERT INTO stone(val) VALUES ('3|3');
INSERT INTO stone(val) VALUES ('3|4');
INSERT INTO stone(val) VALUES ('3|5');
INSERT INTO stone(val) VALUES ('3|6');
INSERT INTO stone(val) VALUES ('4|4');
INSERT INTO stone(val) VALUES ('4|5');
INSERT INTO stone(val) VALUES ('4|6');
INSERT INTO stone(val) VALUES ('5|5');
INSERT INTO stone(val) VALUES ('5|6');
INSERT INTO stone(val) VALUES ('6|6');

INSERT INTO placement(val) VALUES ('LEFT');
INSERT INTO placement(val) VALUES ('RIGHT');

INSERT INTO game_status(val) VALUES ('FINISHED');
INSERT INTO game_status(val) VALUES ('OCCURING');
INSERT INTO game_status(val) VALUES ('CANCELED');
INSERT INTO game_status(val) VALUES ('WAITING');


INSERT INTO users(user_name)
VALUES ('juan'), ('ruisu'), ('milaneso');

INSERT INTO game_session(game_status_id, tstamp)
VALUES (4, 'now');

INSERT INTO player(user_id, game_session_id, turn)
VALUES (1, 1, 1), (2, 1, 2), (3, 1, 3);
COMMIT;
