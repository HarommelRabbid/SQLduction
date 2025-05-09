# SQLduction, a SQL database engine
# By Harommel OddSock
import sys
from functools import lru_cache

tables = []
tabledata = {}

# table functions
class SQLduction:
    def __init__(self):
        pass
    def new(self, name):
        tables.append(name)
        tabledata[name] = {}
    def delete(self, name):
        tables.remove(name)
        tabledata.pop(name, None)
    def find(self, table, key):
        return tabledata[table][key]
    def add(self, table, key, val):
        if val != None:
            tabledata[table][key] = val
        else:
            tabledata[table][key] = None
    def remove(self, table, key):
        tabledata[table].pop(key, None)

# Query tokenizer & parser
class Queryduction:
    keywords = ['NEW', 'DELETE', 'REMOVE', 'LIST', 'FIND', 'ADD', 'EXIT', 'HELP']
    keydescs = ['Creates a new table\nUsage: "NEW [table]"',
                'Deletes a table\nUsage: "DELETE [table]"',
                'Removes an entry from a table\nUsage: "REMOVE [entry] FROM [table]"',
                'Lists all tables or all entries in a table\nUsage: "LIST" or "LIST [table]"',
                'Gets the value of an entry in a table\nUsage: "FIND [entry] IN [table]"',
                'Add an entry in a table, If a value isn\'t set like, then it\'ll default to None\nUsage: "ADD [entry=optional value] TO [table]"',
                'Self-explanatory, exists out of SQLduction',
                'Self-explanatory']
    def __init__(self, command):
        andqueries = command.split('&&')
        if command != '':
            if '&' in command:
                for query in andqueries:
                    self.parser(query)
            else:
                self.parser(command)
    def error(self, reason):
        sys.stderr.write(f'SQLduction has encountered a query error:\n{reason}\n')
    def parser(self, command):
        tokenizer = command.split()
        if not tokenizer[0].upper() in self.keywords:
            self.error(f'"{tokenizer[0]}" is an invalid keyword! Keywords can only be: {", ".join(map(str, self.keywords[:-1])) + " & " + str(self.keywords[-1])}')
        elif not tokenizer[0].isupper():
            self.error(f'"{tokenizer[0]}" is not upper case! Correct is: {tokenizer[0].upper()}')
        else:
            match tokenizer[0]:
                case 'NEW':
                    if len(tokenizer) <= 1:
                        self.error('Table\'s name hasn\'t been defined')
                    elif len(tokenizer) > 2:
                        self.error('Too many arguments')
                    elif tokenizer[1] in tables:
                        self.error(f'Table "{tokenizer[1]}" already exists')
                    else:
                        SQLduction.new(self, tokenizer[1])
                        sys.stdout.write(f'Table "{tokenizer[1]}" has been created\n')
                case 'DELETE':
                    if len(tokenizer) <= 1:
                        self.error('Table\'s name hasn\'t been defined')
                    elif len(tokenizer) > 2:
                        self.error('Too many arguments')
                    elif not tokenizer[1] in tables:
                        self.error(f'Table {tokenizer[1]} doesn\'t exist')
                    else:
                        SQLduction.delete(self, tokenizer[1])
                        sys.stdout.write(f'Table "{tokenizer[1]}" has been deleted\n')
                case 'LIST':
                    @lru_cache
                    def tablelist():
                        if len(tokenizer) > 2:
                            self.error('Too many arguments')
                        else:
                            if len(tokenizer) <= 1:
                                if len(tables) == 0:
                                    sys.stdout.write('There aren\'t any tables made\n')
                                elif len(tables) == 1:
                                    sys.stdout.write(f'The only table is {tables[0]}\n')
                                else:
                                    sys.stdout.write(f'Tables:\n{", ".join(map(str, tables[:-1])) + " & " + str(tables[-1])}\n')
                            else:
                                if not tokenizer[1] in tables:
                                    self.error('Table doesn\'t exist')
                                elif tabledata[tokenizer[1]] == {}:
                                    sys.stdout.write(f"There aren\'t any items in {tokenizer[1]}\n")
                                else:
                                    sys.stdout.write(f"Items of {tokenizer[1]}:\n")
                                    for key, value in tabledata[tokenizer[1]].items():
                                        sys.stdout.write(f"{key}: {value}\n")
                    tablelist()
                case 'ADD':
                    if len(tokenizer) <= 1:
                        self.error('Key name hasn\'t been defined')
                    elif len(tokenizer) <= 2 or tokenizer[2] != "TO":
                        self.error('No TO operator detected in the second argument')
                    elif len(tokenizer) <= 3:
                        self.error('Table\'s name hasn\'t been defined')
                    elif not tokenizer[3] in tables:
                        self.error('Table doesn\'t exist')
                    elif len(tokenizer) > 4:
                        self.error('Too many arguments')
                    else:
                        valtokens = tokenizer[1].split('=')
                        if len(valtokens) == 2:
                            tabledata[tokenizer[3]][valtokens[0]] = valtokens[1]
                            sys.stdout.write(f'Added {valtokens[0]} = {valtokens[1]} to {tokenizer[3]}\n')
                        elif len(valtokens) > 2:
                            self.error('Invalid syntax')
                        else:
                            tabledata[tokenizer[3]][tokenizer[1]] = None
                            sys.stdout.write(f'Added {tokenizer[1]} to {tokenizer[3]}\n')
                case 'REMOVE':
                    if len(tokenizer) <= 1:
                        self.error('Key name hasn\'t been defined')
                    elif len(tokenizer) <= 2 or tokenizer[2] != "FROM":
                        self.error('No FROM operator detected in the second argument')
                    elif len(tokenizer) <= 3:
                        self.error('Table\'s name hasn\'t been defined')
                    elif not tokenizer[3] in tables:
                        self.error('Table doesn\'t exist')
                    elif not tokenizer[1] in tabledata[tokenizer[3]]:
                        self.error(f'"{tokenizer[1]}" doesn\'t exist in {tokenizer[3]}')
                    elif len(tokenizer) > 4:
                        self.error('Too many arguments')
                    else:
                        tabledata[tokenizer[3]].pop(tokenizer[1], None)
                        sys.stdout.write(f'Removed {tokenizer[1]} from {tokenizer[3]}\n')
                case 'FIND':
                    if len(tokenizer) <= 1:
                        self.error('Key name hasn\'t been defined')
                    elif len(tokenizer) <= 2 or tokenizer[2] != "IN":
                        self.error('No IN operator detected in the second argument')
                    elif len(tokenizer) <= 3:
                        self.error('Table\'s name hasn\'t been defined')
                    elif not tokenizer[3] in tables:
                        self.error('Table doesn\'t exist')
                    elif not tokenizer[1] in tabledata[tokenizer[3]]:
                        self.error(f'"{tokenizer[1]}" doesn\'t exist in {tokenizer[3]}')
                    elif len(tokenizer) > 4:
                        self.error('Too many arguments')
                    else:
                        sys.stdout.write(f'{tabledata[tokenizer[3]][tokenizer[1]]}\n')
                case 'HELP':
                    if len(tokenizer) > 1:
                        #self.error('Too many arguments')
                        if tokenizer[1] in self.keywords:
                            sys.stdout.write(f'{tokenizer[1]}: {self.keydescs[self.keywords.index(tokenizer[1])] or ""}\n')
                        else:
                            sys.stderr.write(f'{tokenizer[1]} not found\n')
                    else:
                        sys.stdout.write(f'Help:\nKeywords: {", ".join(map(str, self.keywords[:-1])) + " & " + str(self.keywords[-1])}\nType "HELP [keyword]" to get help with a specific keyword\n')
                case 'EXIT':
                    if len(tokenizer) > 1:
                        self.error('Too many arguments')
                    else:
                        sys.exit()

sys.stdout.write('SQLduction by Harommel OddSock\nType HELP to get started\n\n')
while True:
    Queryduction(input())
