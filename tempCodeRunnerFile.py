def error_handle(self, token_type, value=None):
        if self.current_token and self.current_token['token_name'] == token_type:
            if value is None or self.current_token['pattern'] == value:
                token = self.current_token
                self.advance()
                return token
            else:
                line = self.current_token['line_number']
                col = self.current_token['column_number']
                found = self.current_token['pattern']
                raise Exception(f"Syntax Error at Line {line}, Column {col}: Expected {token_type} {value}, found {found}")
        else:
            line = self.current_token['line_number'] if self.current_token else 'EOF'
            col = self.current_token['column_number'] if self.current_token else ''
            found = self.current_token['pattern'] if self.current_token else 'EOF'
            raise Exception(f"Syntax Error at Line {line}, Column {col}: Expected {token_type}, found {found}")